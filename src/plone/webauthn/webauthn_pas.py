from AccessControl.SecurityInfo import ClassSecurityInfo
from App.config import getConfiguration
from BTrees.OOBTree import OOBTree
from OFS.Cache import Cacheable
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from zope.annotation.interfaces import IAnnotations

import os

from .views.webauthn_login import IWebAuthnLogin

KEY = "plone.webauthn.keys"


prefix = os.path.basename(getConfiguration().clienthome)


manage_addWebauthnPluginForm = PageTemplateFile(
    "www/Add", globals(), __name__="manage_addWebauthnPluginForm"
)


def manage_addWebauthnPlugin(self, id, title="", REQUEST=None):
    """Add a WebauthnPlugin to a Pluggable Authentication Service."""
    c = WebauthnPlugin(id, title)
    self._setObject(c.getId(), c)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect(
            "%s/manage_workspace"
            "?manage_tabs_message="
            "Webauthn+Plugin+added." % self.absolute_url()
        )


class WebauthnPlugin(BasePlugin, Cacheable):
    """Work with extended Onkopedia login credentials and login data service"""

    meta_type = "Webauthn plugin"
    login_path = "login_form"
    security = ClassSecurityInfo()

    manage_options = BasePlugin.manage_options + Cacheable.manage_options

    _properties = ({"id": "title", "label": "Title", "type": "string", "mode": "w"},)

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    @property
    def annotations(self):
        all_annotations = IAnnotations(self)
        if KEY not in all_annotations:
            all_annotations[KEY] = OOBTree()
        return all_annotations[KEY]

    security.declarePrivate("extractCredentials")
    def extractCredentials(self, request):
        print("ExtractCredentials")
        print(request.BODY)
        self.authenticateCredentials(request.BODY)

        return {"login": "ajung", "password": request.BODY}

    security.declarePrivate("authenticateCredentials")
    def authenticateCredentials(self, credentials):
        """Find out if the login and password is correct"""

        print("authenticateCredentials()")
        print("Webauthn credentials:", credentials)

        login_handler = IWebAuthnLogin()

        print("result: ", login_handler.verify_device_for_login(credentials["data"]))

        return None
        return (login, login)


classImplements(
    WebauthnPlugin,
    IAuthenticationPlugin,
    IExtractionPlugin,
)
