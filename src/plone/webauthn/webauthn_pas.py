from AccessControl.SecurityInfo import ClassSecurityInfo
from App.config import getConfiguration
from base64 import decodebytes
from base64 import encodebytes
from loguru import logger as LOG
from OFS.Cache import Cacheable
from pathlib import Path
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import ICredentialsResetPlugin
from Products.PluggableAuthService.interfaces.plugins import ICredentialsUpdatePlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.utils import createKeywords
from Products.PluggableAuthService.utils import createViewName
from urllib.parse import quote
from urllib.parse import unquote

import codecs
import hashlib
import os
import sys
import xmlrpc.client


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

    security.declarePrivate("authenticateCredentials")

    def authenticateCredentials(self, credentials):
        """Find out if the login and password is correct"""

        print("Webauthn credentials:",credentials)
        return None
        return (login, login)


classImplements(
    WebauthnPlugin,
    IAuthenticationPlugin,
)
