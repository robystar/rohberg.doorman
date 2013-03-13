import hashlib
import random
import re
from zope.app.component.hooks import getSite
from Acquisition import aq_base, aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PluggableAuthService.utils import classImplements
from Globals import InitializeClass
from Products.PluggableAuthService.interfaces.plugins import \
    IValidationPlugin, IPropertiesPlugin
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

PLUGIN_ID = 'strengthenedpasswordpasplugin'
PLUGIN_INTERFACES = [IValidationPlugin, IPropertiesPlugin]

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

class StrengthenedPasswordPlugin(BasePlugin):
    ''' Plugin for StrengthenedPassword PAS
    '''
    meta_type = 'StrengthenedPassword PAS'
    security = ClassSecurityInfo()

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
        self._id = self.id = id
        self.title = title

        i = 1
        for reg,err in DEFAULT_POLICIES:
            setattr(self, 'p%i_re' % i, reg)
            setattr(self, 'p%i_err' % i, err)
            i+=1

    def updatePasswordPolicies(self, pplist=None):
        if not isinstance(pplist, list): return
        for item in pplist:
            if not isinstance(item, (list, tuple)): return
            if not len(item)==2: return
        dummy = [(None,"") for i in range(5)]
        for idx, (reg, err) in enumerate((pplist + dummy)[:5]):
            setattr(self, 'p%i_re' % (idx+1), reg)
            setattr(self, 'p%i_err' % (idx+1), err)   
    
    
    security.declarePrivate('validateUserInfo')
    def validateUserInfo(self, user, set_id, set_info ):

        """ -> ( error_info_1, ... error_info_N )

        o Returned values are dictionaries, containing at least keys:

          'id' -- the ID of the property, or None if the error is not
                  specific to one property.

          'error' -- the message string, suitable for display to the user.
        """

        errors = []

        if set_info and set_info.get('password', None) is not None: 
            password = set_info['password']

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

    def getPropertiesForUser(self, user, request=None):
        hash = hashlib.md5(str(random.random())).hexdigest()
        return {'generated_password':'A-'+hash}


for itf in PLUGIN_INTERFACES:
    classImplements(StrengthenedPasswordPlugin, itf)
InitializeClass(StrengthenedPasswordPlugin)