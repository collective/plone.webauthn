# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.webauthn.testing import PLONE_WEBAUTHN_FUNCTIONAL_TESTING
from plone.webauthn.testing import PLONE_WEBAUTHN_INTEGRATION_TESTING
from plone.webauthn.views.key_management import IKeyManagement
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = PLONE_WEBAUTHN_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        api.content.create(self.portal, "Folder", "other-folder")
        api.content.create(self.portal, "Document", "front-page")

    def test_key_management_is_registered(self):
        view = getMultiAdapter(
            (self.portal["other-folder"], self.portal.REQUEST), name="key-management"
        )
        self.assertTrue(IKeyManagement.providedBy(view))

    def test_key_management_not_matching_interface(self):
        view_found = True
        try:
            view = getMultiAdapter(
                (self.portal["front-page"], self.portal.REQUEST), name="key-management"
            )
        except ComponentLookupError:
            view_found = False
        else:
            view_found = IKeyManagement.providedBy(view)
        self.assertFalse(view_found)


class ViewsFunctionalTest(unittest.TestCase):

    layer = PLONE_WEBAUTHN_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
