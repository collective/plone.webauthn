from ..webauthn_pas import manage_addWebauthnPlugin
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.namedfile.file import NamedBlobFile
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.interface import alsoProvides

import os
import plone.api
import sys


PLUGIN_ID = "Webauthn_helper"


def log(msg):
    print(msg)
    sys.stdout.flush()


class InstallPAS(BrowserView):
    def install_all(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.install_pas()
        self.request.response.redirect(self.context.absolute_url())

    def install_pas(self):
        log("\n\nStarting Webauthn plugin installation")
        pas = plone.api.portal.get().acl_users
        plugin_manager = getattr(pas, "plugins")

        if PLUGIN_ID not in pas.objectIds():
            log("- Instantiating Webauthn helper plugin")
            manage_addWebauthnPlugin(pas, PLUGIN_ID, "Webauthn Helper plugin")
        else:
            log("- Webauthn helper plugin already instantiated")

        log("- activating plugin interfaces")
        dgho_plugin = getattr(pas, PLUGIN_ID)
        for interface_name in ("IAuthenticationPlugin",):
            iface = plugin_manager._getInterfaceFromName(interface_name)
            try:
                plugin_manager.activatePlugin(iface, PLUGIN_ID)
                log(f"  - activated interface {interface_name}")
            except KeyError:
                log(f"  - {interface_name} already activated")

        log("Webauthn helper plugin installation complete.\n")

        plone.api.portal.show_message("Webauthn Plugin installed")
