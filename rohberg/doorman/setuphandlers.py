from zope.annotation.interfaces import IAnnotations
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from plugins.doorman import PLUGIN_ID, PLUGIN_INTERFACES, addStrengthenedPasswordPlugin
from plonecontrolpanel import extendSecurityControlPanel, unextendSecurityControlPanel

def setupDoorman(context):
    if context.readDataFile('install_doorman.txt') is None:
        return
    portal = context.getSite()
    installPlugin(portal)
    # extendSecurityControlPanel(portal)
    
def removeDoorman(context):
    if context.readDataFile('uninstall_doorman.txt') is None:
        return
    portal = context.getSite()
    # unextendSecurityControlPanel(portal)
    uninstallPlugin(portal)    
    
    
def installPlugin(portal):
    ''' Install the StrengthenedPasswordPlugin plugin
    '''
    out = StringIO()

    uf = getToolByName(portal, 'acl_users')
    installed = uf.objectIds()

    if PLUGIN_ID not in installed:
        addStrengthenedPasswordPlugin(uf, PLUGIN_ID, 'StrengthenedPassword PAS')
        
        # if portal is already annotated with custom password policy, then use it
        annotations = IAnnotations(portal)
        password_policies = annotations.get('rohberg.doorman.password_policies', None) 
        if password_policies:
            plugin = uf.get(PLUGIN_ID, None)
            if plugin:
                plugin.updatePasswordPolicies(password_policies)        
        
        # plugins = uf.plugins
        # plugins.activatePlugin(IPropertiesPlugin, 'source_users')
        activatePluginInterfaces(portal, PLUGIN_ID, out)
        print >> out, 'strengthenedpasswordpasplugin installed'
    else:
        print >> out, 'strengthenedpasswordpasplugin already installed'
    
    # # source_users deaktivieren, da sonst alle User durchgewunken werden
    # plugins = uf.plugins
    # plugins.deactivatePlugin(IAuthenticationPlugin, 'source_users')

    print out.getvalue()
    
    
def uninstallPlugin(portal):  
    out = StringIO()

    uf = getToolByName(portal, 'acl_users')
    installed = uf.objectIds()

    # plugins = uf.plugins
    # plugins.activatePlugin(IAuthenticationPlugin, 'source_users')

    for itf in PLUGIN_INTERFACES:
        try:
            plugins.deactivatePlugin(itf, PLUGIN_ID)
        except Exception, e:
            print >> out, 'couldnt deactivate %s from %s' % (PLUGIN_ID, itf)
    
    if PLUGIN_ID in installed:
        uf.manage_delObjects(PLUGIN_ID)

    print >> out, 'strengthenedpasswordpasplugin deinstalled'
    
    print out.getvalue()
    