from zope.component import getUtility, getAdapter
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from plone.protect import CheckAuthenticator
from zope.formlib.interfaces import InputErrors
from zope.formlib.interfaces import WidgetInputError

from plone.app.users.browser.register import RegistrationForm as Original_RegistrationForm
from plone.app.users.browser.register import AddUserForm as Original_AddUserForm
from plone.app.users.utils import notifyWidgetActionExecutionError

from Products.CMFPlone import PloneMessageFactory as _

def generate_user_id(self, data):
    """Generate a user id from data.

    The data is the data passed in the form.  Note that when email
    is used as login, the data will not have a username.

    There are plans to add some more options and add a hook here
    so it is possible to use a different scheme here, for example
    creating a uuid or creating bob-jones-1 based on the fullname.

    This will update the 'username' key of the data that is passed.
    """
    default = data.get('username') or data.get('email') or ''
    data['username'] = default
    return default


# Actions validators
def my_validate_registration(self, action, data):
    """Specific business logic for this join form.  Note: all this logic
    was taken directly from the old validate_registration.py script in
    Products/CMFPlone/skins/plone_login/join_form_validate.vpy
    """

    # CSRF protection
    CheckAuthenticator(self.request)

    registration = getToolByName(self.context, 'portal_registration')

    error_keys = [
        error.field.getName()
        for error
        in action.form.widgets.errors
    ]

    form_field_names = [f for f in self.fields]

    portal = getUtility(ISiteRoot)
    portal_props = getToolByName(self.context, 'portal_properties')
    props = portal_props.site_properties
    use_email_as_login = props.getProperty('use_email_as_login')

    # passwords should match
    if 'password' in form_field_names:
        assert('password_ctl' in form_field_names)
        # Skip this check if password fields already have an error
        if not ('password' in error_keys or 'password_ctl' in error_keys):
            password = data.get('password')
            password_ctl = data.get('password_ctl')
            if password != password_ctl:
                err_str = _(u'Passwords do not match.')
                notifyWidgetActionExecutionError(action,
                                                 'password', err_str)
                notifyWidgetActionExecutionError(action,
                                                 'password_ctl', err_str)

    # Password field checked against RegistrationTool
    if 'password' in form_field_names:
        # Skip this check if password fields already have an error
        if 'password' not in error_keys:
            password = data.get('password')
            if password:
                # Use PAS to test validity
                err_str = registration.testPasswordValidity(password)
                if err_str:
                    notifyWidgetActionExecutionError(action,
                                                     'password', err_str)

    if use_email_as_login:
        username_field = 'email'
    else:
        username_field = 'username'

    # The term 'username' is not clear.  It may be the user id or
    # the login name.  So here we try to be explicit.

    # Generate a nice user id and store that in the data.
    user_id = self.generate_user_id(data)
    # Generate a nice login name and store that in the data.
    login_name = self.generate_login_name(data)

    # Do several checks to see if the user id and the login name
    # are valid.
    #
    # Skip these checks if username was already in error list.
    #
    # Note that if we cannot generate a unique user id, it is not
    # necessarily the fault of the username field, but it
    # certainly is the most likely cause in a standard Plone
    # setup.

    # check if username is valid
    # Skip this check if username was already in error list
    if username_field not in error_keys:
        # user id may not be the same as the portal id.
        if user_id == portal.getId():
            err_str = _(u"This username is reserved. Please choose a "
                        "different name.")
            notifyWidgetActionExecutionError(action,
                                             username_field, err_str)

    # Check if user id is allowed by the member id pattern.
    if username_field not in error_keys:
        if not registration.isMemberIdAllowed(user_id):
            err_str = _(u"The login name you selected is already in use "
                        "or is not valid. Please choose another.")
            notifyWidgetActionExecutionError(action,
                                             username_field, err_str)

    if username_field not in error_keys:
        # Check the uniqueness of the login name, not only when
        # use_email_as_login is true, but always.
        pas = getToolByName(self, 'acl_users')
        results = pas.searchUsers(name=login_name, exact_match=True)
        if results:
            err_str = _(u"The login name you selected is already in use "
                        "or is not valid. Please choose another.")
            notifyWidgetActionExecutionError(action,
                                             username_field, err_str)

    if 'password' in form_field_names and 'password' not in error_keys:
        # Admin can either set a password or mail the user (or both).
        if not (data['password'] or data['mail_me']):
            err_str = _('msg_no_password_no_mail_me',
                        default=u"You must set a password or choose to "
                        "send an email.")

            # set error on password field
            notifyWidgetActionExecutionError(action, 'password', err_str)
            notifyWidgetActionExecutionError(action, 'mail_me', err_str)

    
def new_validate_registration(self, action, data, errors = []):
    """
    specific business logic for this join form
    note: all this logic was taken directly from the old
    validate_registration.py script in
    Products/CMFPlone/skins/plone_login/join_form_validate.vpy
    """
    # CSRF protection
    CheckAuthenticator(self.request)


    registration = getToolByName(self.context, 'portal_registration')

    # ConversionErrors have no field_name attribute... :-(
    error_keys = [error.field_name for error in errors
                  if hasattr(error, 'field_name')]

    form_field_names = [f.field.getName() for f in self.form_fields]

    portal = getUtility(ISiteRoot)
    portal_props = getToolByName(self.context, 'portal_properties')
    props = portal_props.site_properties
    use_email_as_login = props.getProperty('use_email_as_login')

    # passwords should match
    if 'password' in form_field_names:
        assert('password_ctl' in form_field_names)
        # Skip this check if password fields already have an error
        if not ('password' in error_keys or \
                'password_ctl' in error_keys):
            password = self.widgets['password'].getInputValue()
            password_ctl = self.widgets['password_ctl'].getInputValue()
            if password != password_ctl:
                err_str = _(u'Passwords do not match.')
                errors.append(WidgetInputError('password',
                              u'label_password', err_str))
                errors.append(WidgetInputError('password_ctl',
                              u'label_password', err_str))
                self.widgets['password'].error = err_str
                self.widgets['password_ctl'].error = err_str

    # changes: Password field should regard custom password_policies
    if 'password' in form_field_names:
        # Skip this check if password fields already have an error
        if not 'password' in error_keys:
            password = self.widgets['password'].getInputValue()
            password_ctl = self.widgets['password_ctl'].getInputValue()
            if password and password_ctl:
                failMessage = registration.testPasswordValidity(password,
                                                                password_ctl)
                if failMessage:
                    errors.append(WidgetInputError('password',
                                      u'label_password', failMessage))
                    errors.append(WidgetInputError('password_ctl',
                                      u'password_ctl', failMessage))
                    self.widgets['password'].error = failMessage
                    self.widgets['password_ctl'].error = failMessage

    username = ''
    email = ''
    try:
        email = self.widgets['email'].getInputValue()
    except InputErrors, exc:
        # WrongType?
        errors.append(exc)
    if use_email_as_login:
        username_field = 'email'
    else:
        username_field = 'username'

    # Generate a nice user id and store that in the data.
    username = self.generate_user_id(data)

    # check if username is valid
    # Skip this check if username was already in error list
    if not username_field in error_keys:
        if username == portal.getId():
            err_str = _(u"This username is reserved. Please choose a "
                        "different name.")
            errors.append(WidgetInputError(
                    username_field, u'label_username', err_str))
            self.widgets[username_field].error = err_str

    # check if username is allowed
    if not username_field in error_keys:
        if not registration.isMemberIdAllowed(username):
            err_str = _(u"The login name you selected is already in use "
                        "or is not valid. Please choose another.")
            errors.append(WidgetInputError(
                    username_field, u'label_username', err_str))
            self.widgets[username_field].error = err_str

    # Skip this check if email was already in error list
    if not 'email' in error_keys:
        if 'email' in form_field_names:
            if not registration.isValidEmail(email):
                err_str = _(u'You must enter a valid email address.')
                errors.append(WidgetInputError(
                        'email', u'label_email', err_str))
                self.widgets['email'].error = err_str

    if use_email_as_login and not 'email' in error_keys:
        pas = getToolByName(self, 'acl_users')
        # maybe search for lowercase as well.
        results = pas.searchUsers(login=email, exact_match=True)
        if results:
            err_str = _(u"The login name you selected is already in use "
                        "or is not valid. Please choose another.")
            errors.append(WidgetInputError(
                    'email', u'label_email', err_str))
            self.widgets['email'].error = err_str

    if 'password' in form_field_names and not 'password' in error_keys:
        # Admin can either set a password or mail the user (or both).
        if not (self.widgets['password'].getInputValue() or
                self.widgets['mail_me'].getInputValue()):
            err_str = _('msg_no_password_no_mail_me',
                        default=u"You must set a password or choose to "
                        "send an email.")
            errors.append(WidgetInputError(
                    'password', u'label_password', err_str))
            self.widgets['password'].error = err_str
            errors.append(WidgetInputError(
                    'mail_me', u'label_mail_me', err_str))
            self.widgets['mail_me'].error = err_str
    return errors
    
    
class RegistrationForm(Original_RegistrationForm):
    
    def validate_registration(self, action, data):        
        return my_validate_registration(self, action, data)
    
class AddUserForm(Original_AddUserForm):

    def validate_registration(self, action, data):        
        return my_validate_registration(self, action, data)

RegistrationForm.generate_user_id = generate_user_id
AddUserForm.generate_user_id = generate_user_id
