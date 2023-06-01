# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import plone.webauthn


class PloneWebauthnLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=plone.webauthn)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.webauthn:default")


PLONE_WEBAUTHN_FIXTURE = PloneWebauthnLayer()


PLONE_WEBAUTHN_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_WEBAUTHN_FIXTURE,),
    name="PloneWebauthnLayer:IntegrationTesting",
)


PLONE_WEBAUTHN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_WEBAUTHN_FIXTURE,),
    name="PloneWebauthnLayer:FunctionalTesting",
)


PLONE_WEBAUTHN_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLONE_WEBAUTHN_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="PloneWebauthnLayer:AcceptanceTesting",
)
