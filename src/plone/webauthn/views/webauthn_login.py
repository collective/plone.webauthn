from ..key_data import IKeyData
from Products.Five.browser import BrowserView
from webauthn.helpers.structs import PublicKeyCredentialDescriptor
from webauthn.helpers.structs import PublicKeyCredentialType
from webauthn.helpers.structs import UserVerificationRequirement
from zope.interface import implementer
from zope.interface import Interface

import base64
import json
import webauthn


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

        if user_id not in list(database.annotations.keys()):
            return json.dumps([])

        credential_names = list(database.annotations[user_id].keys())

        return json.dumps(credential_names)

    def get_authentication_options_for_login(self):
        user_id = self.request["user_id"]
        cname = self.request["cname"]
        user_creds = None

        data_base = IKeyData(self.context)

        if user_id not in data_base.annotations.keys():
            return b'{"error": "No devices registered"}'
        else:
            if cname not in data_base.annotations[user_id].keys():
                return b'{"error": "No devices registered with the device name"}'

        user_creds = data_base.get_user_device_key(user_id, cname)

        try:
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
        except Exception as e:
            message = {"error": "generating authentication options failed: " + str(e) }
            return json.dumps(message)

        self.request.response.setHeader("Content-type", "application/json")

        data = public_key.json()
        data = json.loads(data)
        data["expected_challenge"] = base64.b64encode(public_key.challenge).decode()

        return json.dumps(data)
