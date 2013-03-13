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

regex_password_policy = r'\(u?\'([^\']*?)\',[ ]?u?\'([\w .]+?)\'\)'

class IDoormanSettings(security.ISecuritySchema):
    password_policies = schema.Text(
                title=_(u"Regular Expressions that a password must regard."),
                description=_(u"One expression per line: (u'.{8}.*', u'Minimum 8 characters.')   Default value is %s" % str(DEFAULT_POLICIES)),
                required=False,
                default=default_password_policies)
    password_duration = schema.Int(
                title=_(u"Duration of password validity."),
                description=_(u"Days"),
                required=False,
                default=0)


# password_policies
def get_password_policies(self):
    annotations = IAnnotations(self.portal)
    password_policies = annotations.get('rohberg.doorman.password_policies', [])
    return "\n".join([str(item) for item in password_policies])

def set_password_policies(self, value):
    password_policies = []
    value = value.strip(" \n")
    if value:         
        # test syntax of lines especially regular expression
        for item in value.split("\n"):
            mt = re.match(regex_password_policy, item)
            if mt:
                password_policies.append(mt.group(1,2))
        
    annotations = IAnnotations(self.portal)
    annotations['rohberg.doorman.password_policies'] = password_policies   
    
    plugin = self.portal.acl_users.get(PLUGIN_ID, None)
    if plugin:
        plugin.updatePasswordPolicies(password_policies)


# password_duration
def get_password_duration(self):
    annotations = IAnnotations(self.portal)
    return annotations.get('rohberg.doorman.password_duration', 0)
    
def set_password_duration(self, value):
    annotations = IAnnotations(self.portal)
    annotations['rohberg.doorman.password_duration'] = value   
    # TODO: refresh PAS plugin with password_duration!
    

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
    