import re
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface, Attribute, implementedBy, classImplementsOnly
from zope.component import getGlobalSiteManager
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.formlib.form import FormFields
from plone.app.controlpanel import security
from StringIO import StringIO

from Products.PluggableAuthService.interfaces.plugins import \
    IValidationPlugin
from plugins.doorman import PLUGIN_ID, DEFAULT_POLICIES
from rohberg.doorman import RDMessageFactory as _

default_password_policies = u"" + '/n'.join([str(item) for item in DEFAULT_POLICIES])

regex_password_policy = r'\(u?\'([^\']*?)\',[ ]?u?\'([\w .\-!,]+?)\'\)'

class IDoormanSettings(security.ISecuritySchema):
    password_policies = schema.Text(
                title=_(u"Regular Expressions that a password must regard."),
                description=_(u"One expression per line: (u'.{8}.*', u'Minimum 8 characters.'). Default value is ") + str(DEFAULT_POLICIES),
                required=False,
                default=default_password_policies)
    password_duration = schema.Int(
                title=_(u"Duration of password validity."),
                description=_(u"Days"),
                required=False,
                default=0)
    reject_non_members = schema.Bool(
                title=_(u"Registrierte User, die nicht die Role 'Member' haben, ausschliessen."),
                required=False,
                default=True)
    do_basic_auth_paths = schema.Text(
                title=_(u"Prevent redirect to login page for following paths"),
                description=_(u"One path per line. For example foren/RSS"),
                required=False,
                default=u""
                )


# password_policies
def get_password_policies(self):
    annotations = IAnnotations(self.portal)
    password_policies = annotations.get('rohberg.doorman.password_policies', [])
    return u"" + "\n".join([str(item) for item in password_policies])

def set_password_policies(self, value=u""):
    password_policies = []
    if value:         
        value = value.strip(" \n")
        # test syntax of lines especially regular expression
        for item in value.split("\n"):
            mt = re.match(regex_password_policy, item)
            if mt:
                password_policies.append(mt.group(1,2))
    
    # we constrain to 5 password policy rules
    password_policies = password_policies[:5]
    plugin = self.portal.acl_users.get(PLUGIN_ID, None)
    if plugin:
        plugin.updatePasswordPolicies(password_policies)

    annotations = IAnnotations(self.portal)
    annotations['rohberg.doorman.password_policies'] = password_policies


# password_duration
def get_password_duration(self):
    annotations = IAnnotations(self.portal)
    return annotations.get('rohberg.doorman.password_duration', 0)
    
def set_password_duration(self, value):
    plugin = self.portal.acl_users.get(PLUGIN_ID, None)
    plugin.setPasswordDuration(value)
    annotations = IAnnotations(self.portal)
    annotations['rohberg.doorman.password_duration'] = value
    
# reject_non_members
def get_reject_non_members(self):
    annotations = IAnnotations(self.portal)
    return annotations.get('rohberg.doorman.reject_non_members', True)

def set_reject_non_members(self, value):
    annotations = IAnnotations(self.portal)
    annotations['rohberg.doorman.reject_non_members'] = value

# do_basic_auth_paths
def get_do_basic_auth_paths(self):
    annotations = IAnnotations(self.portal)
    ann = annotations.get('rohberg.doorman.do_basic_auth_paths', [])
    return u"" + "\n".join([str(item) for item in ann])
    
def set_do_basic_auth_paths(self, value):
    items = []
    if value:         
        value = value.strip(" \n")
        items = value.split("\n")

    annotations = IAnnotations(self.portal)
    annotations['rohberg.doorman.do_basic_auth_paths'] = items



def extendSecurityControlPanel(portal=None):     
    out = StringIO()   
    
    security.SecurityControlPanelAdapter.get_password_policies = get_password_policies
    security.SecurityControlPanelAdapter.set_password_policies = set_password_policies
    security.SecurityControlPanelAdapter.password_policies = property(
        security.SecurityControlPanelAdapter.get_password_policies,
        security.SecurityControlPanelAdapter.set_password_policies
        )
    security.SecurityControlPanelAdapter.get_password_duration = get_password_duration
    security.SecurityControlPanelAdapter.set_password_duration = set_password_duration
    security.SecurityControlPanelAdapter.password_duration = property(
        security.SecurityControlPanelAdapter.get_password_duration,
        security.SecurityControlPanelAdapter.set_password_duration
        )
    security.SecurityControlPanelAdapter.get_reject_non_members = get_reject_non_members
    security.SecurityControlPanelAdapter.set_reject_non_members = set_reject_non_members
    security.SecurityControlPanelAdapter.reject_non_members = property(
        security.SecurityControlPanelAdapter.get_reject_non_members,
        security.SecurityControlPanelAdapter.set_reject_non_members
        )
    security.SecurityControlPanelAdapter.get_do_basic_auth_paths = get_do_basic_auth_paths
    security.SecurityControlPanelAdapter.set_do_basic_auth_paths = set_do_basic_auth_paths
    security.SecurityControlPanelAdapter.do_basic_auth_paths = property(
        security.SecurityControlPanelAdapter.get_do_basic_auth_paths,
        security.SecurityControlPanelAdapter.set_do_basic_auth_paths
        )

    # re-register adapter with new interface
    _decl = implementedBy(security.SecurityControlPanelAdapter)
    _decl -= security.ISecuritySchema
    _decl += IDoormanSettings
    classImplementsOnly(security.SecurityControlPanelAdapter, _decl.interfaces())
    del _decl

    getGlobalSiteManager().registerAdapter(security.SecurityControlPanelAdapter)

    # re-instanciate form
    security.SecurityControlPanel.form_fields = FormFields(
        IDoormanSettings
        )
        
    print >> out, 'security control panel extended'
    print out.getvalue()



def unextendSecurityControlPanel(portal=None):
    out = StringIO()    
    
    # re-register adapter with original interface
    _decl = implementedBy(security.SecurityControlPanelAdapter)
    _decl -= IDoormanSettings
    _decl += security.ISecuritySchema
    classImplementsOnly(security.SecurityControlPanelAdapter, _decl.interfaces())
    del _decl

    getGlobalSiteManager().registerAdapter(security.SecurityControlPanelAdapter)

    # re-instanciate form
    security.SecurityControlPanel.form_fields = FormFields(
        security.ISecuritySchema
        )

    print >> out, 'security control panel restauriert'
    print out.getvalue()
    