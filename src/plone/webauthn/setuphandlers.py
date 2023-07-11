# -*- coding: utf-8 -*-
from .webauthn_pas import manage_addWebauthnPlugin
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import plone.api
import sys


PLUGIN_ID = "Webauthn_helper"


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "plone.webauthn:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["plone.webauthn.upgrades"]


def log(msg):
    print(msg)
    sys.stdout.flush()


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.

    def install_pas():
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
        for interface_name in ("IAuthenticationPlugin", "IExtractionPlugin"):
            iface = plugin_manager._getInterfaceFromName(interface_name)
            try:
                plugin_manager.activatePlugin(iface, PLUGIN_ID)
                log(f"  - activated interface {interface_name}")
            except KeyError:
                log(f"  - {interface_name} already activated")

        log("Webauthn helper plugin installation complete.\n")

        plone.api.portal.show_message("Webauthn Plugin installed")

    install_pas()


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
