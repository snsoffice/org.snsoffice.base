# -*- coding: utf-8 -*-
from org.snsoffice.base import _
from org.snsoffice.base.interfaces import IHouse

from Products.Five.browser import BrowserView
from plone.app.content.utils import json_dumps
from plone.app.contenttypes.browser.collection import CollectionView
from Products.CMFPlone.browser.search import Search
from Products.CMFPlone.PloneBatch import Batch
from plone import api

class AnchorHelperView(BrowserView):
    """A simple view to get anchors of one house."""

    def __call__(self):
        self.request.response.setHeader("Content-Type", "application/json")
        return json_dumps({
            'anchors': self.context.anchors
        })

def dump_house(item):
    return {
        'id': item.UID,
        'title': item.Title,
        'description': plone_view.cropText(item.Description, length),
        'source': '/'.join(item.getPhysicalPath()),
        'geometry': item.geometry,
        'geostyle': item.geostyle,
        'state': item.review_state if item.review_state else None,
    }

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
        for item in batch:
            if IHouse.providedBy(item):
                items.append(dump_house(item, prefix))

        prefix = api.portal.get_registry_record('org.snsoffice.base.resource_base_url')
        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps({
            'total': len(results),
            'prefix': prefix,
            'items': items
        })

class CollectionHouseView(CollectionView):

    def __call__(self):
        items = []

        batch = self.batch()
        for item in batch:
            if IHouse.provideBy(item):
                items.append(dump_house(item, prefix))

        prefix = api.portal.get_registry_record('org.snsoffice.base.resource_base_url', '')
        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps({
            'total': len(results),
            'prefix': prefix,
            'items': items
        })

class ImportHelperView(BrowserView):
    """Import outer resource."""

    def __call__(self):
        self.request['_authenticator'] = createToken()
        context = aq_base(self.context)
        form = self.request.form
        status = form.get('status')
        if status is not None:
            context.status = status

        layers = form.get('layers')
        patterns = form.get('patterns')
        res = getAdapter(self.context, IGeoResources)
        if res:
            if layers is not None:
                res.setGeoLayers(json_loads(layers))
            if patterns is not None:
                res.setGeoPatterns(json_loads(patterns))

        self.request.response.setHeader("Content-Type", "application/json")
        return json_dumps({
            'result': 'OK'
        })
