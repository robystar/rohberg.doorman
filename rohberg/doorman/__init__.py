# -*- extra stuff goes here -*-

from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from zope.i18nmessageid import MessageFactory
RDMessageFactory = MessageFactory("rohberg.doorman")

from plugins import doorman

def initialize(context):
    ''' Initialize product
    '''
    registerMultiPlugin(doorman.StrengthenedPasswordPlugin.meta_type) # Add to PAS menu
    context.registerClass(doorman.StrengthenedPasswordPlugin,
                          constructors = (doorman.manage_addStrengthenedPasswordPluginForm,
                                          doorman.addStrengthenedPasswordPlugin),
                          visibility = None)

from rohberg.doorman.plonecontrolpanel import extendSecurityControlPanel
# TODO: Just if rohberg.doorman installed
extendSecurityControlPanel()


from patch import \
    patchTestPasswordValidity, patchGetPassword, patchMailPassword
patchTestPasswordValidity()
patchGetPassword()
patchMailPassword()
