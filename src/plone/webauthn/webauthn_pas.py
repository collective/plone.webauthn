from AccessControl.SecurityInfo import ClassSecurityInfo
from App.config import getConfiguration
from BTrees.OOBTree import OOBTree
from OFS.Cache import Cacheable
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from zope.interface import Interface
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection

import os
import json
import base64
import webauthn

from .key_data import IKeyData
from .key_data import KEY


prefix = os.path.basename(getConfiguration().clienthome)


manage_addWebauthnPluginForm = PageTemplateFile(
    "www/Add", globals(), __name__= "manage_addWebauthnPluginForm"
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
        annos = self.annotations # ensure that OOBTree is initialized properly

    @property
    def annotations(self):
        annotations = getattr(self, KEY, None)
        if annotations is None:
            setattr(self, KEY, OOBTree())
            annotations = getattr(self, KEY)
        return annotations

    security.declarePrivate("extractCredentials")
    def extractCredentials(self, request):

        return {"login": "ajung", "password": request.BODY}

    security.declarePrivate("authenticateCredentials")
    def authenticateCredentials(self, credentials):
        """Find out if the login and password is correct"""
        data = credentials["password"].decode('utf-8')
        data = data[data.find("form_data")+len("form_data="): data.find("&buttons.login")]


        data = data.replace("%7B", "{")
        data = data.replace("%22", "\"")
        data = data.replace("%3A", ":")
        data = data.replace("%2C", ",")
        data = data.replace("%2B", "+")
        data = data.replace("%3D", "=")
        data = data.replace("%2F", "/")
        data = data.replace("%7D", "}")

        data = json.loads(data)
        user_id = data["user_id"]
        cname = data["cname"]

        data_base = IKeyData("nthg")
        user_creds = data_base.get_user_device_key(user_id, cname)

        data["raw_id"] = base64.urlsafe_b64decode(data["raw_id"])
        data["response"]["authenticator_data"] = data["response"]["authenticatorData"]
        del data["response"]["authenticatorData"]

        for key in data["response"].keys():
            data["response"][key] = base64.urlsafe_b64decode(data["response"][key])

        credentials = webauthn.helpers.structs.AuthenticationCredential(
            id = data["id"],
            raw_id = data["raw_id"],
            response = data["response"]
        )
        
        expected_challenge = base64.urlsafe_b64decode( data["challenge"])

        try:
            auth = webauthn.verify_authentication_response(  # type: ignore
                credential=credentials,
                expected_challenge=expected_challenge,
                expected_rp_id="localhost",
                expected_origin="http://localhost:8080",
                credential_public_key=user_creds["public_key"],
                credential_current_sign_count=user_creds["sign_count"],
            )
        except:
            return (None, None)

        #data_base.update_key(user_id, cname, {"sign_count": auth.new_sign_count})

        return (user_id, user_id)


classImplements(
    WebauthnPlugin,
    IAuthenticationPlugin,
    IExtractionPlugin,
)
