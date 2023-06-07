# -*- coding: utf-8 -*-

# from plone.webauthn import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

import webauthn
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

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

ATTESTATION_TYPE_MAPPING = {
    "none": AttestationConveyancePreference.NONE,
    "indirect": AttestationConveyancePreference.INDIRECT,
    "direct": AttestationConveyancePreference.DIRECT,
}

AUTH_MAPPING = {
    "cross-platform": AuthenticatorAttachment.CROSS_PLATFORM,
    "platform": AuthenticatorAttachment.PLATFORM,
}


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
    
    def register_device(self):
        print(self.request)

        attestation_type = "direct"
        authenticator_type = "platform"


        public_key = webauthn.generate_registration_options(  # type: ignore
            rp_id="localhost",
            rp_name="MyCompanyName",
            user_id= "pavab",
            user_name= "pavan@example.com",
            user_display_name="Samuel Colvin",
            attestation=ATTESTATION_TYPE_MAPPING[attestation_type],
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AUTH_MAPPING[authenticator_type]
                if authenticator_type
                else AuthenticatorAttachment.CROSS_PLATFORM,
                resident_key=ResidentKeyRequirement.DISCOURAGED,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )
    
        #request.session["webauthn_register_challenge"] = base64.b64encode(public_key.challenge).decode()
    
        return public_key