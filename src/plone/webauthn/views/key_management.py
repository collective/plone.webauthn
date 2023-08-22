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

        try:
            public_key = webauthn.generate_registration_options(  # type: ignore
                rp_id="localhost",
                rp_name="Plone",
                user_id=cname,
                user_name=user_id,
                user_display_name=user_id + "-" + cname,
                attestation=ATTESTATION_TYPE_MAPPING[attestation_type],
                authenticator_selection=AuthenticatorSelectionCriteria(
                    authenticator_attachment=AUTH_MAPPING[authenticator_type]
                    if authenticator_type
                    else AuthenticatorAttachment.CROSS_PLATFORM,
                    resident_key=ResidentKeyRequirement.DISCOURAGED,
                    user_verification=UserVerificationRequirement.REQUIRED,
                ),
            )
        except:
            return b'{"error": "generating registration options failed"}'

        self.request.response.setHeader("Content-type", "application/json")

        data = public_key.json()
        data = json.loads(data)
        data["expected_challenge"] = base64.b64encode(public_key.challenge).decode()

        return json.dumps(data)

    def add_device(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json.loads(self.request["BODY"].decode("utf-8"))
        data["raw_id"] = base64.urlsafe_b64decode(data["raw_id"])

        for key in data["response"].keys():
            data["response"][key] = base64.urlsafe_b64decode(data["response"][key])

        credentials = webauthn.helpers.structs.RegistrationCredential(
            id=data["id"], raw_id=data["raw_id"], response=data["response"]
        )

        expected_challenge = base64.urlsafe_b64decode(data["challenge"])

        try:
            registration = webauthn.verify_registration_response(  # type: ignore
                credential=credentials,
                expected_challenge=expected_challenge,
                expected_rp_id="localhost",
                expected_origin="http://localhost:8080",
            )
        except:
            return b'{"error": "verifying registration failed"}'

        data = {
            "public_key": registration.credential_public_key,
            "sign_count": registration.sign_count,
            "credential_id": registration.credential_id,
            "challenge": expected_challenge,
        }

        data_base = IKeyData(self.context)
        user_id = str(plone.api.user.get_current())
        cname = self.request["cname"]
        data_base.add_key(user_id, cname, data)

        return b'{"result": "success"}'

    def get_keys_for_user(self):
        user_id = str(plone.api.user.get_current())

        database = IKeyData(self.context)

        if user_id not in list(database.annotations.keys()):
            return json.dumps([])

        credential_names = list(database.annotations[user_id].keys())

        return json.dumps(credential_names)

    def delete_credential(self):
        database = IKeyData(self.context)

        user_id = str(plone.api.user.get_current())
        cname = self.request["cname"]

        del database.annotations[user_id][cname]
        database.annotations._p_changed = 1

        return b"{message: deleted}"

    def delete_all(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        database = IKeyData(self.context)

        database.remove_all()
