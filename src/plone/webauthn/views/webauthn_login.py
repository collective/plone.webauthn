from zope.interface import implementer
from zope.interface import Interface
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection

from ..key_data import IKeyData
import json
import base64
import plone.api
import webauthn

from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
    UserVerificationRequirement,
)

class IWebAuthnLogin(Interface):
    """Marker Interface for IKeyManagement"""


@implementer(IWebAuthnLogin)
class WebAuthnLogin(BrowserView):

    def __call__(self):
        # Implement your own actions:
        return self.index()
    
    def get_keys_for_login(self):
        user_id = self.request["user_id"]

        database = IKeyData(self.context)

        if user_id not in list(database.keys.keys()):
            return json.dumps([])
        
        credential_names = list(database.keys[user_id].keys())

        return json.dumps(credential_names)
    
    def get_authentication_options_for_login(self):
        user_id = self.request["user_id"]
        cname = self.request["cname"]
        user_creds = None

        data_base = IKeyData(self.context)

        if user_id not in data_base.keys.keys():
            return b'{"error": "No devices registered"}'
        else:
            if cname not in data_base.keys[user_id].keys():
                return b'{"error": "No devices registered with the device name"}'

        user_creds = data_base.get_user_device_key(user_id, cname)
        
        public_key = webauthn.generate_authentication_options(  # type: ignore
            rp_id="localhost",
            timeout=50000,
            allow_credentials=[
                PublicKeyCredentialDescriptor(
                    type=PublicKeyCredentialType.PUBLIC_KEY,
                    id=user_creds["credential_id"],
                )
            ],
            user_verification=UserVerificationRequirement.DISCOURAGED,
            )
        
        self.request.response.setHeader("Content-type", "application/json")

        data = public_key.json()
        data = json.loads(data)
        data["expected_challenge"] = base64.b64encode(public_key.challenge).decode()

        return json.dumps(data)
    
    def verify_device_for_login(self, body):
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json.loads(body.decode('utf-8'))

        user_id = data["user_id"]
        cname = data["cname"]
        data_base = IKeyData(self.context)
        user_creds = data_base.get_user_device_key(user_id, cname)

        data = json.loads(self.request["BODY"].decode('utf-8'))
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

        auth = webauthn.verify_authentication_response(  # type: ignore
            credential=credentials,
            expected_challenge=expected_challenge,
            expected_rp_id="localhost",
            expected_origin="http://localhost:8080",
            credential_public_key=user_creds["public_key"],
            credential_current_sign_count=user_creds["sign_count"],
        )
        print(auth)

        data_base.update_key(user_id, cname, {"sign_count": auth.new_sign_count})

        return b'{"result": "success"}'