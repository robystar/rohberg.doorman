from AccessControl.SecurityManagement import noSecurityManager
from Products.statusmessages.interfaces import IStatusMessage

# TODO: Ajax. redirect von Login boexli funktioniert noch nicht

# logout and redirect to reset password form
# 

# Python imports
import logging
from DateTime import DateTime

# ZODB imports
from ZODB.POSException import ConflictError

# Zope imports
from AccessControl import getSecurityManager
from zope.interface import Interface
from zope.component import getUtility
from zope.app.component.hooks import getSite

# CMFCore imports
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent

# Caveman imports
from five import grok

# Plone imports
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from plugins.doorman import PLUGIN_ID

# Logger output for this module
logger = logging.getLogger(__name__)

from rohberg.doorman import RDMessageFactory as _

def redirect_to_loggedout_reset_password(user):
    """
    Redirects the user to reset password form

    :return: True or False depending if we found a redirect target or not
    """
    portal = getSite()

    username = user.getId()
    
    def isPasswordDurationExpired(portal, member):
        username = user.getId()        
        if username == "admin": return False  
        
        plugin = portal.acl_users.get(PLUGIN_ID, None)
        password_duration = plugin.getPasswordDuration()
        # if no password_duration defined or password_duration == 0: no password reset neccessary
        if password_duration < 1:
            return False
        last_password_reset = member.getProperty('last_password_reset')
        jetzt = DateTime()
        cond = last_password_reset+password_duration < jetzt
        if cond:
            return True
        return False
        
    def getPasswordResetURL(portal, username):
        reset_tool = getToolByName(portal, 'portal_password_reset')
        reset = reset_tool.requestReset(username)
        url = "%s/passwordreset/%s?userid=%s" % (portal.absolute_url(), reset.get('randomstring',""), username)
        return url
    
    request = getattr(portal, "REQUEST", None)
    if not request:
        return False

    sm = getSecurityManager()

    
    if isPasswordDurationExpired(portal, user):
        # logout:
        noSecurityManager()
        logger.info("Redirecting user %s to reset password form %s" % (username, getPasswordResetURL(portal, username)))
        
        msg = _(u"Your password is expired. Please reset your password.")
        IStatusMessage(request).addStatusMessage(msg, type='error')
        
        request.response.redirect(getPasswordResetURL(portal, username))
        return True

    # Let the normal login proceed to the page "You are now logged in" etc.
    return False


@grok.subscribe(IUserLoggedInEvent)
def logged_in_handler(event):
    """
    Listen to the event and perform the action accordingly.
    """

    user = event.object

    redirect_to_loggedout_reset_password(user)
