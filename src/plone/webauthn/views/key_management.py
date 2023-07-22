# -*- coding: utf-8 -*-

# from plone.webauthn import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection

import json
import webauthn
import base64
import plone.api

from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticationCredential,
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialCreationOptions,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialRequestOptions,
    PublicKeyCredentialType,
    RegistrationCredential,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from webauthn.helpers import (
    aaguid_to_string,
    bytes_to_base64url,
    decode_credential_public_key,
    parse_attestation_object,
    parse_client_data_json,
    parse_backup_flags,
)

from ..key_data import IKeyData

ATTESTATION_TYPE_MAPPING = {
    "none": AttestationConveyancePreference.NONE,
    "indirect": AttestationConveyancePreference.INDIRECT,
    "direct": AttestationConveyancePreference.DIRECT,
}


AUTH_MAPPING = {
    "cross-platform": AuthenticatorAttachment.CROSS_PLATFORM,
    "platform": AuthenticatorAttachment.PLATFORM,
}


# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IKeyManagement(Interface):
    """Marker Interface for IKeyManagement"""


@implementer(IKeyManagement)
class KeyManagement(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('key_management.pt')


    def __call__(self):
        # Implement your own actions:
        return self.index()
    
    def get_registration_options(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        attestation_type = self.request["attestation_type"]
        authenticator_type = self.request["authenticator_type"]
        cname = self.request["cname"]
        user_id = str(plone.api.user.get_current())

        data_base = IKeyData(self.context)

        if user_id in list(data_base.annotations.keys()):
            if cname in list(data_base.annotations[user_id].keys()):
                return b'{"error": "device already registered"}'

        public_key = webauthn.generate_registration_options(  # type: ignore
            rp_id = "localhost",
            rp_name = "Plone",
            user_id = cname,
            user_name = user_id,
            user_display_name = user_id+"-"+cname,
            attestation = ATTESTATION_TYPE_MAPPING[attestation_type],
            
            authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AUTH_MAPPING[authenticator_type]
            if authenticator_type
            else AuthenticatorAttachment.CROSS_PLATFORM,
            resident_key=ResidentKeyRequirement.DISCOURAGED,
            user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )

        self.request.response.setHeader("Content-type", "application/json")

        data = public_key.json()
        data = json.loads(data)
        data["expected_challenge"] = base64.b64encode(public_key.challenge).decode()

        return json.dumps(data)
    

    def add_device(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        print(self.request)

        data = json.loads(self.request["BODY"].decode('utf-8'))
        data["raw_id"] = base64.urlsafe_b64decode(data["raw_id"])

        for key in data["response"].keys():
            data["response"][key] = base64.urlsafe_b64decode(data["response"][key])

        credentials = webauthn.helpers.structs.RegistrationCredential(
            id = data["id"],
            raw_id = data["raw_id"],
            response = data["response"]
        )

        expected_challenge = base64.urlsafe_b64decode( data["challenge"])
        
        registration = webauthn.verify_registration_response(  # type: ignore
            credential = credentials,
            expected_challenge = expected_challenge,
            expected_rp_id = "localhost",
            expected_origin = "http://localhost:8080",
        )

        data = {
            "public_key": registration.credential_public_key,
            "sign_count": registration.sign_count,
            "credential_id": registration.credential_id,
            "challenge": expected_challenge,
        }

        print("registration complete need to add to database.")

        data_base = IKeyData(self.context)
        user_id = str(plone.api.user.get_current())
        cname = self.request["cname"]
        data_base.add_key(user_id, cname, data)

        print(f"key added to database with cname: {self.request['cname']}")

        return b'{"result": "success"}'
    


    def get_authentication_options(self):
        user_id = str(plone.api.user.get_current())
        cname = self.request["cname"]
        user_creds = None

        data_base = IKeyData(self.context)

        if user_id not in data_base.annotations.keys():
            return b'{"error": "No devices registered"}'
        else:
            if cname not in data_base.annotations[user_id].keys():
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
    


    def verify_device(self):

        alsoProvides(self.request, IDisableCSRFProtection)

        user_id = str(plone.api.user.get_current())
        cname = self.request["cname"]
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

        print("##################################################################")
        print(credentials)
        print(expected_challenge)
        print(user_creds)
        print("########################################################")

        auth = webauthn.verify_authentication_response(  # type: ignore
            credential=credentials,
            expected_challenge=expected_challenge,
            expected_rp_id="localhost",
            expected_origin="http://localhost:8080",
            credential_public_key=user_creds["public_key"],
            credential_current_sign_count=user_creds["sign_count"],
        )

        data_base.update_key(user_id, cname, {"sign_count": auth.new_sign_count})

        return b'{"result": "success"}'
    
    def get_keys_for_user(self):
        user_id = str(plone.api.user.get_current())

        database = IKeyData(self.context)

        if user_id not in list(database.annotations.keys()):
            return json.dumps([])
        
        credential_names = list(database.annotations[user_id].keys())

        return json.dumps(credential_names)
    
    def delete_credential(self):

        print("here", self.request)
        database = IKeyData(self.context)

        user_id = str(plone.api.user.get_current())
        cname = self.request["cname"]

        print(user_id,cname)

        del database.annotations[user_id][cname]
        database.annotations._p_changed = 1

        return b"{message: deleted}"
        
    
    def delete_all(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        database = IKeyData(self.context)

        user_id = str(plone.api.user.get_current())

        for key in list(database.annotations.keys()):
            del database.annotations[key]

        print(list(database.annotations.keys()))

        for key in list(database.annotations.keys()):
            print(key, database.annotations[key])

    def work(self):
        database = IKeyData(self.context)
        for key in list(database.keys.keys()):
            print(key, database.keys[key])
        



