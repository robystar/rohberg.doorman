from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.testing import z2

from zope.configuration import xmlconfig

class RohbergDoormanLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)
    
    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import rohberg.doorman
        # xmlconfig.file('configure.zcml',
        #        rohberg.doorman,
        #        context=configurationContext
        #        )
        self.loadZCML(package=rohberg.doorman)
        z2.installProduct(app, 'rohberg.doorman')
               
    def setUpPloneSite(self, portal):
            applyProfile(portal, 'rohberg.doorman:default')
    
    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'rohberg.doorman')
            
ROHBERG_DOORMAN_FIXTURE = RohbergDoormanLayer()
ROHBERG_DOORMAN_INTEGRATION_TESTING = IntegrationTesting(
        bases=(ROHBERG_DOORMAN_FIXTURE,),
        name="Rohberg:Integration"
        )
ROHBERG_DOORMAN_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(ROHBERG_DOORMAN_FIXTURE,),
        name="Rohberg:Functional"
        )
