from zope.annotation.interfaces import IAnnotations
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from plugins.doorman import PLUGIN_ID, DEFAULT_POLICIES, PLUGIN_INTERFACES, addStrengthenedPasswordPlugin
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
    zope_pas = portal.getPhysicalRoot().acl_users
    installed = uf.objectIds()

    if PLUGIN_ID not in installed:
        annotations = IAnnotations(portal)
        annotations['rohberg.doorman.password_policies'] =\
            annotations.get('rohberg.doorman.password_policies', None) or DEFAULT_POLICIES
        annotations['rohberg.doorman.password_duration'] =\
            annotations.get('rohberg.doorman.password_duration', None) or 0
        
        addStrengthenedPasswordPlugin(uf, PLUGIN_ID, 'StrengthenedPassword PAS')
        
        # if portal is already annotated with custom password policy, then use it
        plugin = uf.get(PLUGIN_ID, None)
        if plugin:
            password_policies = annotations.get('rohberg.doorman.password_policies', DEFAULT_POLICIES) 
            plugin.updatePasswordPolicies(password_policies)      
            password_duration = annotations.get('rohberg.doorman.password_duration', 0)
            plugin.setPasswordDuration(password_duration)
        
        # plugins = uf.plugins
        # plugins.activatePlugin(IValidationPlugin, 'source_users')
        activatePluginInterfaces(portal, PLUGIN_ID, out)
        
        # define which interfaces need to be moved to top of plugin list
        move_to_top_interfaces = [
            (uf, 'IChallengePlugin'),
            (uf, 'IAuthenticationPlugin'),
            # zope_pas: 'IAnonymousUserFactoryPlugin',
            ]
        for (pas, interface) in move_to_top_interfaces:
            movePluginToTop(pas, PLUGIN_ID, interface, out)
            print >> out, "moved %s to top" % interface
            
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


def movePluginToTop(pas, plugin_id, interface_name, out):
    #because default plone properties plugin mask any other,
    #you must place it before it
    iface = pas.plugins._getInterfaceFromName(interface_name)
    pluginids = pas.plugins.listPluginIds(iface)
    plugin_index = pluginids.index(plugin_id)
    for i in range(plugin_index):
        pas.plugins.movePluginsUp(iface, [plugin_id])