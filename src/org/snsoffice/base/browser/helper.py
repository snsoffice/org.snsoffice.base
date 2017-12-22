# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from Products.Five.browser import BrowserView
from plone.app.content.utils import json_dumps
from plone.app.contenttypes.browser.collection import CollectionView
from Products.CMFPlone.browser.search import Search
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.browser.navtree import getNavigationRoot
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component import getUtility

class AnchorHelperView(BrowserView):
    """A simple view to get anchors of one house."""

    def __call__(self):
        self.request.response.setHeader("Content-Type", "application/json")
        return json_dumps({
            'anchors': self.context.anchors
        })

class AjaxHouseSearch(Search):
    """SearchableText, portal_type, path, show_inactive, sort_on, sort_order, sort_limit"""

    def __call__(self):
        items = []
        try:
            per_page = int(self.request.form.get('perPage'))
        except:
            per_page = 10
        try:
            page = int(self.request.form.get('page'))
        except:
            page = 1

        results = self.results(batch=False, use_content_listing=False)
        batch = Batch(results, per_page, start=(page - 1) * per_page)

        registry = queryUtility(IRegistry)
        length = registry.get('plone.search_results_description_length')
        plone_view = getMultiAdapter(
            (self.context, self.request), name='plone')
        registry = getUtility(IRegistry)
        view_action_types = registry.get(
            'plone.types_use_view_action_in_listings', [])
        for item in batch:
            url = item.getURL()
            if item.portal_type in view_action_types:
                url = '%s/view' % url
            items.append({
                'id': item.UID,
                'title': item.Title,
                'description': plone_view.cropText(item.Description, length),
                'url': url,
                'state': item.review_state if item.review_state else None,
            })
        return json.dumps({
            'total': len(results),
            'items': items
        })

class CollectionHouseView(CollectionView):

    def __call__(self):
        items = []
        batch = self.batch()

        registry = queryUtility(IRegistry)
        length = registry.get('plone.search_results_description_length')
        plone_view = getMultiAdapter(
            (self.context, self.request), name='plone')
        registry = getUtility(IRegistry)
        view_action_types = registry.get(
            'plone.types_use_view_action_in_listings', [])
        for item in batch:
            url = item.getURL()
            if item.portal_type in view_action_types:
                url = '%s/view' % url
            items.append({
                'id': item.UID,
                'title': item.Title,
                'description': plone_view.cropText(item.Description, length),
                'url': url,
                'state': item.review_state if item.review_state else None,
            })
        return json.dumps({
            'total': len(results),
            'items': items
        })
