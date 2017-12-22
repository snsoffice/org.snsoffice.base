# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from Products.Five.browser import BrowserView
from plone.app.content.utils import json_dumps

class AnchorHelperView(BrowserView):
    """A simple view to get anchors of one house."""

    def __call__(self):
        self.request.response.setHeader("Content-Type", "application/json")
        return json_dumps({
            'anchors': self.context.anchors
        })
