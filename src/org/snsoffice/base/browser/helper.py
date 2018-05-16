# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from plone.app.content.utils import json_dumps
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from zope.component import getMultiAdapter
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five import BrowserView

from zope import schema
from zope.interface import Interface
from z3c.form import button
from z3c.form import form
from z3c.form import field

from org.snsoffice.base.interfaces import IHouseFeature
from org.snsoffice.base.interfaces import IHouseView
from org.snsoffice.base.interfaces import ISpot
from org.snsoffice.base.interfaces import IFloor
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

class GeoView(BrowserView):

    def __call__(self):
        return super(GeoView, self).__call__()

class BuildView(BrowserView):

    def __call__(self):
        # self.upload(self.build())
        # return super(BuildView, self).__call__()
        return json_dumps(self.build())

    def upload(self, data):
        bucket_name = 'plone-house'
        key = getSiteRootRelativePath(self.context, self.request) + '/config.json'
        ret, info = uploadData(json_dumps(data), bucket_name, key)
        message = _(u'Build successfully.')
        IStatusMessage(self.request).addStatusMessage(message, 'info')

    def build(self):
        context = self.context
        result = {
            'name': context.getId(),
            'title': context.title,
            'origin': [0, 0],
            'views': list(),
            'features': list(),
            'children': list(),
        }

        if IGeoFeature.providedBy(context):
            if hasattr(context, 'geoextent'):
                result['extent'] = [float(x) for x in context.geoextent.split(',')]
            if hasattr(context, 'geolocation'):
                result['origin'] = [float(x) for x in context.geolocation.split(',')]

        if (IContentish.providedBy(context) or IFolderish.providedBy(context)):
            for v in context.contentValues():
                if IHouseView.providedBy(v):
                    item = {
                        'type': v.view_type,
                        'opacity': v.opacity,
                        'extent': [float(x) for x in v.geoextent.split(',')],
                        'url': v.source,
                    }
                    result['views'].append(item)

                elif IHouseFeature.providedBy(v):
                    item = {
                        'type': v.phase_type,
                        'location': [float(x) for x in v.geolocation.split(',')],
                        'angle': v.geoangle,
                        'url': v.source,
                    }
                    result['features'].append(item)

                elif IFloor.providedBy(v):
                    elevations = result.get('elevations')
                    if elevations is None:
                        elevations = list()
                        result['elevations'] = elevations
                    elevations.append(v.getId())

                elif ISpot.providedBy(v):
                    item = {
                        # 如果是一个链接，那么需要使用 .. 方式表示出来
                        # 例如 ../rooms/1701
                        'name': v.getId(),
                        'origin': [float(x) for x in v.geolocation.split(',')],
                        'extent': [float(x) for x in v.geoextent.split(',')],
                    }
                    result['children'].append(item)

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
