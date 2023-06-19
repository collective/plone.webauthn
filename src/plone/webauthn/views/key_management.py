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

from base64 import urlsafe_b64encode

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

        print(self.request.keys())

        attestation_type = self.request["attestation_type"]

        print(attestation_type)

        authenticator_type = self.request["authenticator_type"]

        print(authenticator_type)

        public_key = webauthn.generate_registration_options(  # type: ignore
            rp_id = "localhost",
            rp_name = "MyCompanyName",
            user_id = self.request["user_id"],
            user_name = "pavan@example.com",
            user_display_name = "Pavan Thota",
            attestation = ATTESTATION_TYPE_MAPPING[attestation_type],
            
            authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AUTH_MAPPING[authenticator_type]
            if authenticator_type
            else AuthenticatorAttachment.CROSS_PLATFORM,
            resident_key=ResidentKeyRequirement.DISCOURAGED,
            user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )

        print(base64.b64encode(public_key.challenge).decode())

        #self.request["SESSION"] = {"webauthn_register_challenge": base64.b64encode(public_key.challenge).decode()}
        #self.request.session["webauthn_register_challenge"] = base64.b64encode(public_key.challenge).decode()

        print(type(public_key))

        self.request.response.setHeader("Content-type", "application/json")

        data = public_key.json()

        data = json.loads(data)

        data["expected_challenge"] = base64.b64encode(public_key.challenge).decode()



        return json.dumps(data)
    
    def b64decode(self, s: str) -> bytes:
        return base64.urlsafe_b64decode(s.encode())
    
    def test(self, val: bytes):
        data = json.loads(val)
    

    def add_device(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        print(self.request["BODY"])

        data = json.loads(self.request["BODY"].decode('utf-8'))
        
        print(data)

        data["raw_id"] = base64.urlsafe_b64decode(data["raw_id"])

        for key in data["response"].keys():
            data["response"][key] = base64.urlsafe_b64decode(data["response"][key])


        credentials = webauthn.helpers.structs.RegistrationCredential(
            id = data["id"],
            raw_id = data["raw_id"],
            response = data["response"]
        )
        


        expected_challenge = base64.urlsafe_b64decode( data["challenge"].encode())
        
        registration = webauthn.verify_registration_response(  # type: ignore
            credential = credentials,
            expected_challenge = data["challenge"],
            expected_rp_id = "localhost",
            expected_origin = "http://localhost:8000",
        )

        auth_database[self.request["id"]] = {
            "public_key": registration.credential_public_key,
            "sign_count": registration.sign_count,
            "credential_id": registration.credential_id,
            "challenge": expected_challenge,
        }

        print("registration complete need to add to databse.")

