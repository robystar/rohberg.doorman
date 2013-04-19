import hashlib
import random
import re
# import datetime
from DateTime import DateTime
from zope.site.hooks import getSite
from Acquisition import aq_base, aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
# from Products.PluggableAuthService.plugins.ZODBUserManager import \
#     ZODBUserManager as BasePlugin
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from AccessControl import ClassSecurityInfo, AuthEncoding
from Products.PluggableAuthService.utils import classImplements
from Globals import InitializeClass
from Products.PluggableAuthService.interfaces.plugins import \
    IValidationPlugin, IAuthenticationPlugin, IChallengePlugin
from Products.PlonePAS.interfaces.plugins import \
    IUserManagement
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from rohberg.doorman import RDMessageFactory as _

import logging
log = logging.getLogger('doorman PAS Plugin')

PLUGIN_ID = 'strengthenedpasswordpasplugin'
PLUGIN_INTERFACES = [IValidationPlugin, IUserManagement] 
# IAuthenticationPlugin, IChallengePlugin

DEFAULT_POLICIES = [(u'.{8}.*','Minimum 8 characters.')
                    ,(u'.*[A-Z].*','Minimum 1 capital letter.')
                    ,(u'.*[a-z].*','Minimum 1 lower case letter.')
                    ,(u'.*[0-9].*','Minimum 1 number.')
                    ,(u'.*[^0-9a-zA-Z ].*','Minimum 1 non-alpha character.')
                    ]


manage_addStrengthenedPasswordPluginForm = PageTemplateFile('addStrengthenedPasswordPAS',
    globals(), __name__='manage_addStrengthenedPasswordPluginForm')

def addStrengthenedPasswordPlugin(self, id, title='', REQUEST=None):
    ''' Add StrengthenedPasswordPlugin to Plone PAS
    '''
    o = StrengthenedPasswordPlugin(id, title)
    self._setObject(o.getId(), o)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_main'
            '?manage_tabs_message=StrengthenedPassword+PAS+Plugin+added.' %
            self.absolute_url())

#  TODO: make plugin Cachable
class StrengthenedPasswordPlugin(BasePlugin):
    ''' Plugin for StrengthenedPassword PAS
    custom password policy
    force password reset after configured time
    '''
    meta_type = 'StrengthenedPassword PAS'
    security = ClassSecurityInfo()
    password_duration = 0

    _properties = ( { 'id'    : 'title'
                    , 'label' : 'Title'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p1_re'
                    , 'label' : 'Policy 1 Regular Expression'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p1_err'
                    , 'label' : 'Policy 1 Error Message'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p2_re'
                    , 'label' : 'Policy 2 Regular Expression'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p2_err'
                    , 'label' : 'Policy 2 Error Message'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p3_re'
                    , 'label' : 'Policy 3 Regular Expression'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p3_err'
                    , 'label' : 'Policy 3 Error Message'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p4_re'
                    , 'label' : 'Policy 4 Regular Expression'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p4_err'
                    , 'label' : 'Policy 4 Error Message'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p5_re'
                    , 'label' : 'Policy 5 Regular Expression'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'p5_err'
                    , 'label' : 'Policy 5 Error Message'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  )


    def __init__(self, id, title=None):
        # super(StrengthenedPasswordPlugin, self).__init__(id, title)
        self._id = self.id = id
        self.title = title

        i = 1
        for reg,err in DEFAULT_POLICIES:
            setattr(self, 'p%i_re' % i, reg)
            setattr(self, 'p%i_err' % i, err)
            i+=1

    def updatePasswordPolicies(self, pplist=None):
        """pplist: list of tuples: (regular expression, error message)"""
        error_message = "argument has to be list of tuples: (regular expression, error message)"
        if not isinstance(pplist, list): raise TypeError(error_message)
        for item in pplist:
            if not isinstance(item, (list, tuple)): raise TypeError(error_message)
            if not len(item)==2: raise TypeError(error_message)
        dummy = [(None,"") for i in range(5)]
        for idx, (reg, err) in enumerate((pplist + dummy)[:5]):
            setattr(self, 'p%i_re' % (idx+1), reg)
            setattr(self, 'p%i_err' % (idx+1), err)   
    
    def setPasswordDuration(self, password_duration):
        if not isinstance(password_duration, int):
            raise TypeError("password_duration must be integer.")
        setattr(self, "password_duration", password_duration)
    
    def getPasswordDuration(self):
        return getattr(self, "password_duration", 0)
        
    # def isPasswordDurationExpired(self, username):
    #     password_duration = getattr(self, "password_duration", 0)
    #     # if no password_duration defined or password_duration == 0: no password reset neccessary
    #     if password_duration < 1:
    #         return False
    #     mt = getToolByName(self, 'portal_membership')
    #     member = mt.getMemberById(username)
    #     last_password_reset = member.getProperty('last_password_reset')
    #     jetzt = DateTime()
    #     cond = last_password_reset+password_duration < jetzt
    #     if cond:
    #         return True
    #     return False
    
    security.declarePrivate('validateUserInfo')
    def validateUserInfo(self, user, set_id, set_info ):

        """ called when user resets password
        
        -> ( error_info_1, ... error_info_N )

        o Returned values are dictionaries, containing at least keys:

          'id' -- the ID of the property, or None if the error is not
                  specific to one property.

          'error' -- the message string, suitable for display to the user.
        """

        errors = []

        if set_info and set_info.get('password', None) is not None: 
            password = set_info['password']
            
            # # TODO: how to compare old and new password? 
            # # principal_id = ?
            # acl_users = aq_parent(self)
            # ups = acl_users.source_users._user_passwords
            # reference = ups.get(principal_id)
            # if reference: 
            #     if AuthEncoding.pw_validate(reference, password):
            #         errors += [_(u"New password has to differ from old one.")]

            i = 1
            while True:
                reg = getattr(self, 'p%i_re' % i, None)
                if not reg:
                    break
                if not re.match(reg, password):
                    err = getattr(self, 'p%i_err' % i, None)
                    errors += [err]
                i += 1

            errors = [{'id':'password','error':e} for e in errors] 
        
        return errors


    security.declarePrivate('doChangeUser')
    def doChangeUser(self, principal_id, password):
        """ Do not change a user's password but 
        (notify if this is done or )
        modify user property last_password_reset
        
        IUserManagement(plugins.IUserAdderPlugin)
        """
        mt = getToolByName(self, 'portal_membership')
        member = mt.getMemberById(principal_id)
        user = member
        # acl_users = aq_parent(self)
        # user = acl_users.getUserById(principal_id)
                
        if user is None:
            raise RuntimeError("User does not exist: %s" % principal_id)
        
        jetzt = DateTime() # datetime.date.today()  
        user.setMemberProperties({'last_password_reset': jetzt})
    
    # see postlogin.py
    # security.declarePrivate('authenticateCredentials')
    # def authenticateCredentials(self, credentials):
    #     """ credentials -> (userid, login)
    # 
    #     o 'credentials' will be a mapping, as returned by IExtractionPlugin.
    # 
    #     o Return a  tuple consisting of user ID (which may be different
    #       from the login name) and login
    # 
    #     o If the credentials cannot be authenticated, return None.
    #     """
    #     request = self.REQUEST
    #     response = request['RESPONSE']
    # 
    #     login = credentials.get('login')
    #     password = credentials.get('password')
    # 
    #     print "authenticateCredentials for %s" % login
    #     if None in (login, password):
    #         return None
    #     
    #     if login == "admin": return None
    #         
    #     if self.isPasswordDurationExpired(login):
    #         request['portal_status_message'] = (
    #                 "This account is locked."
    #                 "Please reset your password.")
    #         request['locked_login'] = login # so challenge plugin can fire
    #         # request.set('__ac','') #HACK - need ot reset in current request not just reponse like cookie auth does
    #         # self.resetAllCredentials(request, response) # must reset so we don't lockout of the login page
    #         
    #         log.info("Attempt denied due to password duration: %s",login)
    #         # raise Unauthorized
    #         return (login,login)
    #         return None
    #         
    #     return None
    
    
    # see postlogin.py
    # security.declarePrivate('challenge')
    # def challenge(self, request, response):
    #     """ Assert via the response that credentials will be gathered.
    # 
    #     Takes a REQUEST object and a RESPONSE object.
    # 
    #     Returns True if it fired, False otherwise.
    # 
    #     Two common ways to initiate a challenge:
    # 
    #       - Add a 'WWW-Authenticate' header to the response object.
    # 
    #         NOTE: add, since the HTTP spec specifically allows for
    #         more than one challenge in a given response.
    # 
    #       - Cause the response object to redirect to another URL (a
    #         login form page, for instance)
    #     """
    #     # redirect to passwordreset/xyz 
    #     login = request.get('locked_login', None)
    #     if login == "admin": return False
    #     print "doorman challenge for %s " % str(login)
    #     if login and self.isPasswordDurationExpired(login):
    #         return self.resetPassword(login)
    #     return False
    #     
    # security.declarePrivate('resetPassword')
    # def resetPassword(self, username):
    #     req = self.REQUEST
    #     resp = req['RESPONSE']
    # 
    #     # Redirect if desired.
    #     url = self.getPasswordResetURL(username)
    #     if url is not None:
    #         resp.redirect(url, lock=1)
    #         return True
    # 
    #     # Could not challenge.
    #     return False
    #  
    # security.declarePrivate('doChangeUser')
    # def getPasswordResetURL(self, username):
    #     reset_tool = getToolByName(self, 'portal_password_reset')
    #     reset = reset_tool.requestReset(username)
    #     url = "%s/passwordreset/%s" % (self.portal.absolute_url(), reset)
    #     print "getPasswordResetURL", url
    #     return url   
        
for itf in PLUGIN_INTERFACES:
    classImplements(StrengthenedPasswordPlugin, itf)
InitializeClass(StrengthenedPasswordPlugin)