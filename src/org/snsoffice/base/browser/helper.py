# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from Acquisition import aq_inner
from plone.app.content.utils import json_dumps
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from Products.Five import BrowserView
from Products.Five.utilities.interfaces import IMarkerInterfaces
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from zope import schema
from zope.component import getMultiAdapter
from z3c.form import button
from z3c.form import form
from z3c.form import field
from zope.interface import Interface

from org.snsoffice.base.interfaces import ISpot
from org.snsoffice.base.interfaces import IOrganization
from org.snsoffice.base.interfaces import IHouse
from org.snsoffice.base.interfaces import IHouseFeature
from org.snsoffice.base.interfaces import IHouseView
from org.snsoffice.base.interfaces import IPublicHouse
from org.snsoffice.base.interfaces import PUBLIC_DOMAIN
from org.snsoffice.base.interfaces import HOUSE_DOMAIN_PARAMETER
from org.snsoffice.base.geo import IGeoFeature
from org.snsoffice.base.cloud import makeToken
from org.snsoffice.base.cloud import uploadData
from org.snsoffice.base.cloud import deleteCloudResource
from org.snsoffice.base.cloud import listCloudResource

class HelperView(BrowserView):

    def __call__(self):
        return super(HelperView, self).__call__()


class AppView(BrowserView):

    def __call__(self):
        pt = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state'
        )
        if pt.anonymous():
            url = pt.portal_url() + '/applogin'
            self.request.response.redirect(url)
        else:
            member = pt.member()
            userid = member.getId()

            mt = getToolByName(self.context, 'portal_membership')
            mi = mt.getMemberInfo(userid)

            fullname = mi.get('fullname', userid)
            self.username = fullname if fullname else userid

            self.user_title = self.context.translate(
                _(u'Login as %s')) % self.username.decode('utf-8')
            self.userid = userid

            self.upload_options = json_dumps(self.get_upload_options(mt))
            self.select2_options = json_dumps(self.get_select2_options(pt))
            self.related_options = json_dumps(self.get_related_options(pt))

        return super(AppView, self).__call__()

    def get_upload_options(self, mt):
        """Upload view options."""
        options = {
            'url': '/upload',
            'currentPath': mt.getHomeUrl()
        }
        return options

    def get_select2_options(self, pt):
        base_url = pt.portal_url()
        vocabulary = '%s/@@getVocabulary?name=' % base_url
        return {
            'vocabularyUrl': '%splone.app.vocabularies.Users' % vocabulary
        }

    def get_related_options(self, pt):
        base_url = pt.portal_url()
        vocabulary = '%s/@@getVocabulary?name=' % base_url
        return {
            'maximumSelectionSize': 1,
            'vocabularyUrl': '%splone.app.vocabularies.Catalog' % vocabulary
        }


class IConnectForm(Interface):
    """ Define form fields """

    friend = schema.Choice(
        title=_(u"label_friend", default=u"Friend"),
        vocabulary="plone.app.vocabularies.Users",
        required=True,
    )

    link = schema.URI(
        title=_(u"Link", default=u"Link"),
        required=True,
    )

    # content = RelationChoice(
    #     title=_(u"Document"),
    #     vocabulary="plone.app.vocabularies.Catalog",
    #     required=False,
    # )


class ConnectForm(form.Form):
    """ Define Form handling """

    ignoreContext = True
    schema = IConnectForm

    label = _(u'conntect_form_title', default=u'Collaborator')
    fields = field.Fields(IConnectForm)

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do something with valid data here

        # Set status on this form page
        # (this status message is not bind to the session and does not go thru redirects)
        self.status = "Thank you very much!"

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """

def getSiteRootRelativePath(context, request):
    portal_state = getMultiAdapter((context, request), name='plone_portal_state')
    site = portal_state.portal()

    # Both of these are tuples
    site_path = site.getPhysicalPath()
    context_path = context.getPhysicalPath()

    relative_path = context_path[len(site_path):]
    return '/'.join(relative_path)

class AnchorHelperView(BrowserView):

    def __call__(self):
        return super(AnchorHelperView, self).__call__()

class ImportView(BrowserView):

    def __call__(self):
        return super(ImportView, self).__call__()


class UploadView(BrowserView):

    def items(self):
        key_preifx = getSiteRootRelativePath(self.context, self.request)
        bucket_name = 'plone-house'
        return listCloudResource(bucket_name, key_preifx)

    def __call__(self):
        return super(UploadView, self).__call__()

class PublicHouseHelper(BrowserView):

    def __call__(self):
        obj = aq_inner(self.context)
        adapter = IMarkerInterfaces(obj)
        adapter.update(add=(IPublicHouse,))
        return json_dumps({
            'id': self.context.getId(),
            'title': self.context.title_or_id(),
            'path': self.context.getPhysicalPath(),
            'url': self.context.absolute_url(),
        })

class UserinfoHelper(BrowserView):

    def __init__(self, context, request):
        super(UserinfoHelper, self).__init__(context, request)
        self.pas_member = getMultiAdapter(
            (context, request), name=u"pas_member")

    def __call__(self):
        userid = self.request.form.get('userid')
        member = self.pas_member.info(userid)
        result = {
            'id': userid,
            'fullname': member['name_or_id'],
            'location': member['location'],
            'description': member['description'],
            'portrait': member.get('portrait', ''),
            'home_page': member['home_page'],
        }
        return json_dumps(result)

class GeoLocator(BrowserView):

    def __call__(self):
        return super(GeoLocator, self).__call__()

class ConfigHelper(BrowserView):

    def __call__(self):
        userid = self.request.form.get(HOUSE_DOMAIN_PARAMETER)
        # self.upload(self.build())
        return json_dumps(self.build_config(userid))

    def upload(self, data):
        bucket_name = 'plone-house'
        key = getSiteRootRelativePath(self.context, self.request) + '/config.json'
        ret, info = uploadData(json_dumps(data), bucket_name, key)
        message = _(u'Build successfully.')
        IStatusMessage(self.request).addStatusMessage(message, 'info')

    def get_locations(self, context):
        locations = []
        obj = self.building.to_object
        while True:
            locations.append('/'.join(obj.getPhysicalPath()))
            if IOrganization.providedBy(obj):
                break
            obj = obj.__parent__
        locations.reverse()
        return ' - '.join(locations)

    def build_views(self, context):
        portal_catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(context.getPhysicalPath())
        brains = portal_catalog.searchResults(
            portal_type=('HouseView',),
            path={'query': path, 'depth': 1},
        )
        views = []
        for brain in brains:
            v = brain.getObject()
            views.append({
                'name': v.getId(),
                'type': v.view_type,
                'opacity': v.opacity,
                'geometry': v.geometry,
                'url': self.build_views(v)
            })

    def build_view_url(self, view):
        src = view.source
        if not src:
            images = api.content.find(
                context=view,
                depth=1,
                portal_type='Image',
            )
            if images:
                return images[0].absolute_url()
        elif src.startswith('http://') or str.startswith('https://'):
            return src
        else:
            return view.absolute_url() + '/' + src

    def build_locations(self, context):
        results = []
        building = context.building.to_object
        while True:
            views = []
            for v in building.contentValues():
                if IHouseView.providedBy(v):
                    url = self.build_view_url(v)
                    if url is None:
                        continue
                    views.append({
                        'name': v.getId(),
                        'type': v.view_type,
                        'opacity': v.opacity,
                        'geometry': v.geometry,
                        'url': url
                    })
            results.append( { 'views': views } )

            if IOrganization.providedBy(building):
                break
            building = building.__parent__

        return results

    def build_config(self, userid=None):
        context = self.context
        result = {
            'name': context.getId(),
            'type': context.portal_type,
            'title': context.title,
            'description': context.Description(),
            'creator': context.Creator(),
            'coordinate': [0, 0],
            'views': list(),
            'features': list(),
            'children': list(),
        }

        if IHouse.providedBy(context):
            result['metadata'] = {
                'house_location': context.house_location(),
                'house_area': context.house_area(),
                'house_type': context.house_type,
                'floor': context.floor,
            }
            result['locations'] = self.build_locations(context)

        if hasattr(context, 'geometry') and context.geometry is not None:
            result['geometry'] = context.geometry
        if hasattr(context, 'coordinate') and context.coordinate is not None:
            result['coordinate'] = context.coordinate

        if (IContentish.providedBy(context) or IFolderish.providedBy(context)):
            for v in context.contentValues():
                if IHouseView.providedBy(v):
                    url = self.build_view_url(v)
                    if url is None:
                        continue
                    item = {
                        'name': v.getId(),
                        'type': v.view_type,
                        'opacity': v.opacity,
                        'geometry': v.geometry,
                        'url': url
                    }
                    result['views'].append(item)

                elif IHouseFeature.providedBy(v):
                    if v.source is None:
                        contentFilter = { "portal_type" : "Image" }
                        images = v.getFolderContents(contentFilter, batch=True, b_size=1)
                        url = images[0].getURL() if len(images) else None
                    else:
                        url = v.absolute_url() + '/' + v.source
                    result['features'].append({
                        'name': v.getId(),
                        'phase_type': v.phase_type,
                        'coordinate': v.coordinate,
                        'angle': v.geoangle,
                        'url': url,
                    })

                elif IHouse.providedBy(v):
                    if (userid and userid == v.Creator()) or PUBLIC_DOMAIN in v.Subject():
                        result['children'].append({
                            'name': v.getId(),
                            'title': v.title,
                            'type': v.portal_type,
                            'floor': v.floor,
                            'coordinate': v.coordinate,
                            'geometry': v.geometry
                        })

                elif ISpot.providedBy(v):
                    result['children'].append({
                        'name': v.getId(),
                        'title': v.title,
                        'type': v.portal_type,
                        'coordinate': v.coordinate,
                        'geometry': v.geometry
                    })

        return result

class UploadTokenView(BrowserView):

    def __call__(self):
        bucket_name = 'plone-house'
        key_prefix = getSiteRootRelativePath(self.context, self.request)
        token = makeToken(bucket_name, key_prefix)
        result = dict(token=token)
        return json_dumps(result)

class RemoveResourceView(BrowserView):

    def __call__(self):
        bucket_name = 'plone-house'
        key = self.request.get('key')
        deleteCloudResource(bucket_name, key)
        return json_dumps({
            'result': 0
        })
