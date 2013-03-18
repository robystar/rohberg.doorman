import transaction
import unittest2 as unittest
# import datetime
from DateTime import DateTime

from zope.component import getSiteManager
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost

from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import login, setRoles
from plone.testing.z2 import Browser

from Products.PluggableAuthService.interfaces.plugins import\
    IValidationPlugin, IAuthenticationPlugin

from rohberg.doorman.testing import \
    ROHBERG_DOORMAN_INTEGRATION_TESTING, ROHBERG_DOORMAN_FUNCTIONAL_TESTING,\
    VANILLA_FUNCTIONAL_TESTING
from plugins.doorman import PLUGIN_ID, DEFAULT_POLICIES

username = "user1"
weakpassword        = '12345'
strongpassword      = '1dOOrman!' # good for default_policies, not good enough for custom_policies
strongpassword2     = '2dOOrman!'
strongerpassword    = '3dOOrman!3'

def validate(validators, user, password):
    # Password is valid if all validators return no errors
    set_info = {'password': password}
    result = []
    for vid, validator in validators:
        result = validator.validateUserInfo(user, None, set_info)
        if result != []:
            break
    return result
    

class DoormanTestCase(unittest.TestCase):

    layer = ROHBERG_DOORMAN_INTEGRATION_TESTING

    def test_passwordstrength_default_policy(self):
        portal = self.layer['portal']
        acl_users = getToolByName(portal, 'acl_users')
        validators = acl_users.plugins.listPlugins(IValidationPlugin)

        acl_users.userFolderAddUser(username, strongpassword, ['Member'], [])
        user = acl_users.getUserById(username)
        
        # We log in with weak password, and we will not be authenticated.
        acl_users.userSetPassword(username, weakpassword)
        self.assertNotEqual(validate(validators, user, weakpassword), [])
        
        # Then we log in with strong password, and we will be authenticated.
        acl_users.userSetPassword(username, strongpassword)
        self.assertEqual(validate(validators, user, strongpassword), [])


def browserLogin(portal, browser, username=None, password=None):
    handleErrors = browser.handleErrors
    try:
        browser.handleErrors = False
        browser.open(portal.absolute_url() + '/login_form')
        if username is None:
            username = TEST_USER_NAME
        if password is None:
            password = TEST_USER_PASSWORD
        browser.getControl(name='__ac_name').value = username
        browser.getControl(name='__ac_password').value = password
        browser.getControl(name='submit').click()
    finally:
        browser.handleErrors = handleErrors  
              
class DoormanFunctionalTestCase(unittest.TestCase):

    layer = ROHBERG_DOORMAN_FUNCTIONAL_TESTING    

    def setUp(self):
        super(DoormanFunctionalTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.portalURL = self.portal.absolute_url()
        self.app = self.layer['app']
        self.acl_users = getToolByName(self.portal, 'acl_users')   
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()
        login(self.portal, TEST_USER_NAME)              

    def test_resetpassword_default_policy(self):
        """ user changes own password
        """
        browser = Browser(self.app) 
        browser.handleErrors = False
        browserLogin(self.portal, browser, TEST_USER_NAME, TEST_USER_PASSWORD)
        
        browser.open(self.portalURL + "/@@change-password")
        
        # First we try a weak password
        browser.getControl(name='form.current_password').value = TEST_USER_PASSWORD
        browser.getControl(name='form.new_password').value = weakpassword
        browser.getControl(name='form.new_password_ctl').value = weakpassword
        browser.getControl(name='form.actions.reset_passwd').click()
        self.assertTrue('Password changed' not in browser.contents) 
        self.assertTrue(DEFAULT_POLICIES[0][1] in browser.contents)      
        
        # Then we change the password to a strong password
        browser.getControl(name='form.current_password').value = TEST_USER_PASSWORD
        browser.getControl(name='form.new_password').value = strongpassword
        browser.getControl(name='form.new_password_ctl').value = strongpassword
        browser.getControl(name='form.actions.reset_passwd').click()
        self.assertTrue('Password changed' in browser.contents)
        
        

class ControlPanelTestCase(unittest.TestCase):

    layer = ROHBERG_DOORMAN_FUNCTIONAL_TESTING

    def setUp(self):
        super(ControlPanelTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.portalURL = self.portal.absolute_url()
        self.app = self.layer['app']
        self.acl_users = getToolByName(self.portal, 'acl_users')   
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()
        login(self.portal, TEST_USER_NAME)
        self.browser = Browser(self.app) 
        self.browser.handleErrors = False 
        
        # mailhost 
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # We need to fake a valid mail setup
        self.portal.email_from_address = "portal@plone.test"
        self.mailhost = self.portal.MailHost
        
    def test_custom_password_policy(self):
        """ Change password policy in security control panel
        """     
    
        browser = self.browser
        browserLogin(self.portal, browser, TEST_USER_NAME, TEST_USER_PASSWORD)
        browser.open(self.portalURL+"/@@security-controlpanel")
        browser.getControl(name='form.password_policies').value = """('.{10}.*', 'Minimum 10 characters.')
('.*[A-Z].*', 'Minimum 1 capital letter.')
('.*[a-z].*', 'Minimum 1 lower case letter.')
('.*[0-9].*', 'Minimum 1 number.')"""
        browser.getControl(name='form.actions.save').click()
        
        #  now we change our password
        browser.open(self.portalURL + "/@@change-password")
        
        # First we try a weak password
        browser.getControl(name='form.current_password').value = TEST_USER_PASSWORD
        browser.getControl(name='form.new_password').value = strongpassword
        browser.getControl(name='form.new_password_ctl').value = strongpassword
        browser.getControl(name='form.actions.reset_passwd').click()
        self.assertFalse('Password changed' in browser.contents)   
        self.assertTrue('Minimum 10 characters.' in browser.contents)  
        
        # Then we change the password to a strong password
        browser.getControl(name='form.current_password').value = TEST_USER_PASSWORD
        browser.getControl(name='form.new_password').value = strongerpassword
        browser.getControl(name='form.new_password_ctl').value = strongerpassword
        browser.getControl(name='form.actions.reset_passwd').click()
        self.assertTrue('Password changed' in browser.contents)        
        
        
            
    def test_add_user(self):
        browserLogin(self.portal, self.browser, TEST_USER_NAME, TEST_USER_PASSWORD)
        
        self.browser.open(self.portalURL + '/new-user')
        self.browser.getControl('User Name').value = 'newuser'
        self.browser.getControl('E-mail').value = 'newuser@example.com'
        self.browser.getControl('Password').value = weakpassword
        self.browser.getControl('Confirm password').value = weakpassword
        self.browser.getControl('Site Administrators').selected = True
        self.browser.getControl('Register').click()
        
        # User is not registered with weak password
        self.assertFalse("User added" in self.browser.contents)
        
        self.browser.open(self.portalURL + '/new-user')
        self.browser.getControl('User Name').value = 'newuser'
        self.browser.getControl('E-mail').value = 'newuser@example.com'
        self.browser.getControl('Password').value = strongpassword
        self.browser.getControl('Confirm password').value = strongpassword
        self.browser.getControl('Site Administrators').selected = True
        self.browser.getControl('Register').click()
        
        # The new user is registered 
        self.assertTrue("User added" in self.browser.contents)
        
         
class DurationTestCase(unittest.TestCase):
    
    layer = ROHBERG_DOORMAN_INTEGRATION_TESTING
    
    def setUp(self):
        super(DurationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.acl_users = getToolByName(self.portal, 'acl_users')   
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # login(self.portal, TEST_USER_NAME)
        self.membership = getToolByName(self.portal, 'portal_membership')
        
    def testProperties(self):
        self.portal.portal_registration.addMember(username, strongpassword)
        member = self.membership.getMemberById(username)
        nie = DateTime('2000/01/01 00:00:00')
                
        self.assertEqual(member.getProperty('last_password_reset'), nie)
        self.acl_users.userSetPassword(username, strongerpassword)
        member = self.membership.getMemberById(username)
        self.assertNotEqual(member.getProperty('last_password_reset'), nie)
        
        
class DurationTestCase2(unittest.TestCase):
    
    layer = ROHBERG_DOORMAN_FUNCTIONAL_TESTING
    
    def setUp(self):
        super(DurationTestCase2, self).setUp()
        self.portal = self.layer['portal']
        self.portalURL = self.portal.absolute_url()
        self.app = self.layer['app']
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.browser = Browser(self.app) 
        self.browser.handleErrors = False
        self.membership = self.portal.portal_membership
        
    def test_password_duration(self):         
        # add user (username, strongpassword)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.acl_users.userFolderAddUser(username, strongpassword, ['Member'], [])
        setRoles(self.portal, TEST_USER_ID, ['Member'])
                
        # set password_duration to 1 day
        plugin = self.portal.acl_users.get(PLUGIN_ID, None)        
        plugin.setPasswordDuration(1)
        
        # before we go to browser:
        transaction.commit() 
        browser = Browser(self.app)
        
        # we are not able to log in
        browserLogin(self.portal, browser, username, strongpassword)
        self.assertFalse("logged in" in browser.contents)
        
        # reset password
        # start password reset procedure and get passwordreset url
        reset_tool = getToolByName(self.portal, 'portal_password_reset')
        reset = reset_tool.requestReset(username)
        passwordreset_url = "%s/passwordreset/%s?userid=%s" % (self.portal.absolute_url(), reset.get('randomstring',""), username)
        # before we go back to browser:
        transaction.commit() 
        browser = Browser(self.app)
        browser.open(passwordreset_url)
        self.assertEqual(browser.url, passwordreset_url)        
        
        browser.getControl(name='password').value = strongerpassword
        browser.getControl(name='password2').value = strongerpassword
        browser.getControl('Set my password').click()
        self.assertTrue('Your password has been set successfully.' in browser.contents)
        
        # now we log in
        browserLogin(self.portal, browser, username, strongerpassword)
        self.assertTrue("logged in" in browser.contents)
        
    def test_password_duration_default(self):
        # add user (username, strongpassword)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.acl_users.userFolderAddUser(username, strongpassword, ['Member'], [])
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        
        transaction.commit() 
        browser = Browser(self.app)
        
        # we are able to log in, if no password_duration ist defined
        browserLogin(self.portal, browser, username, strongpassword)
        self.assertTrue("logged in" in browser.contents)

    def test_reject_non_member(self):
        # add user (username, strongpassword)
        setRoles(self.portal, TEST_USER_ID, ['Manager']    )
        self.acl_users.userFolderAddUser(username, strongpassword, [], [])
        # setRoles(self.portal, TEST_USER_ID, ['Member'])        
        
        transaction.commit() 
        browser = Browser(self.app)
        
        # we are not able to log in without Role "Member"
        browserLogin(self.portal, browser, username, strongpassword)
        self.assertFalse("logged in" in browser.contents)
        
        browserLogin(self.portal, browser, TEST_USER_NAME, TEST_USER_PASSWORD)        
        login(self.portal, TEST_USER_NAME)
        browser.open(self.portalURL+"/@@security-controlpanel")
        # print browser.contents
        browser.getControl(name='form.reject_non_members').value = False
        browser.getControl(name='form.actions.save').click()
        
        browser.open(self.portalURL + "/logout") 
        
        transaction.commit() 
        browser = Browser(self.app)       
        
        # now we are able to log in without Role "Member"
        browserLogin(self.portal, browser, username, strongpassword)
        self.assertTrue("logged in" in browser.contents)
        