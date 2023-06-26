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


auth_database = {}

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
        user_id = self.request["user_id"]

        data_base = IKeyData(self.context)

        if user_id in list(data_base.keys.keys()):
            return b'{"error": "user exists"}'

        public_key = webauthn.generate_registration_options(  # type: ignore
            rp_id = "localhost",
            rp_name = "Plone",
            user_id = user_id,
            user_name = user_id,
            user_display_name = user_id,
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

        print("registration complete need to add to databse.")

        # wrong: self.context = your Plone site
        # but you want to store the data on the object of the PAS Plugin
        # import plone.api
        # data_base = plone.api.portal.get().restrictedTraverse("acl_users/Webauthn_helper")
        #data_base = IKeyData(plone.api.portal.get().restrictedTraverse("acl_users/Webauthn_helper"))
        #TypeError: ('Could not adapt', <WebauthnPlugin at /Plone/acl_users/Webauthn_helper>, <InterfaceClass zope.annotation.interfaces.IAnnotations>)

        data_base = IKeyData(self.context)
        data_base.add_key(self.request["user_id"], data)

        print(f"key added to database with user id: {self.request['user_id']}")

        return b'{"result": "success"}'
    


    def get_authentication_options(self):
        user_id = self.request["user_id"]
        user_creds = None

        data_base = IKeyData(self.context)

        try:
            user_creds = data_base.get_key_by_user_id(self.request["user_id"])[0]
        except ValueError:
            return b'{"error": "user not found"}'
        
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

        user_id = self.request["user_id"]
        data_base = IKeyData(self.context)
        user_creds = None

        if user_id not in list(data_base.keys.keys()):
            return b'{"error": "user not found"}'
        else:
            user_creds = data_base.get_key_by_user_id(user_id)[0]

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

        data_base.update_key(user_id, {"sign_count": auth.new_sign_count})

        return b'{"result": "success"}'
    
    def get_all_data(self):
        data_base = IKeyData(self.context)

        print(list(data_base.annotations.keys()))

        for k in list(data_base.annotations.keys()):
            print(k)

        

        return data_base.annotations



