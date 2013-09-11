from zope.annotation.interfaces import IAnnotations
from AccessControl.SecurityManagement import noSecurityManager
from Products.statusmessages.interfaces import IStatusMessage

# from AccessControl import Unauthorized

# TODO: Ajax. Redirect von Login box fails

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
from zope.component.hooks import getSite

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
    request = getattr(portal, "REQUEST", None)
    if not request:
        return False
    username = user.getId()
    
    def isPasswordDurationExpired(portal, member):
        try:
            member.getUserId()
        except:    
            return False
                
        plugin = portal.acl_users.get(PLUGIN_ID, None)
        if not plugin:
            return False
        password_duration = plugin.getPasswordDuration()
        # if no password_duration defined or password_duration == 0: no password reset neccessary
        if password_duration < 1:
            return False
        jetzt = DateTime()
        last_password_reset = member.getProperty('last_password_reset', jetzt-1000)
        cond = last_password_reset+password_duration < jetzt
        if cond:
            return True
        return False
        
    def getPasswordResetURL(portal, username):
        reset_tool = getToolByName(portal, 'portal_password_reset')
        reset = reset_tool.requestReset(username)
        url = u"%s/passwordreset/%s?userid=%s" % (portal.absolute_url(), reset.get('randomstring',""), username)
        return url



    # reject non-members and redirect to info page
    annotations = IAnnotations(portal)
    reject_non_members = annotations.get('rohberg.doorman.reject_non_members', True)
    if reject_non_members:
        if not user.has_role('Member') and not user.has_role('Manager'):
            # logout:
            noSecurityManager()
            logger.info("Redirecting non-member %s to info page" % username)

            msg = _(u"Your account is locked.")
            portal.plone_utils.addPortalMessage(msg, type='info')

            url = portal.absolute_url() + "/login"
            return request.response.redirect(url)

    
    if isPasswordDurationExpired(portal, user):
        # logout:
        noSecurityManager()
        url = getPasswordResetURL(portal, username)
        logger.info("Redirecting user %s to reset password form %s" % (username, url))
        
        msg = _(u"Your password is expired. Please reset your password.")
        portal.plone_utils.addPortalMessage(msg, type='error')
        
        request.response.redirect(url)
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
    