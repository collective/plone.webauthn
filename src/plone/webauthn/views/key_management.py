# -*- coding: utf-8 -*-

# from plone.webauthn import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface


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
