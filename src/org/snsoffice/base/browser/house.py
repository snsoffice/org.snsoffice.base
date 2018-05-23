# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.permissions import AddPortalContent
from Products.Five.browser import BrowserView
from plone.app.dexterity.interfaces import IDXFileFactory
from plone.dexterity.interfaces import IDexterityFTI
from plone.uuid.interfaces import IUUID

import json
import logging
import mimetypes
import os
from zipfile import ZipFile

from Acquisition import aq_inner
from zope.component import getAdapter
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.protect import CheckAuthenticator
from zope.publisher.browser import BrowserPage
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from plone.dexterity.events import AddCancelledEvent
from zope.event import notify
from z3c.form import button
from plone.z3cform import layout
from plone.dexterity.browser.add import DefaultAddForm
from z3c.relationfield.schema import RelationChoice
from plone.app.vocabularies.catalog import CatalogSource
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import directlyProvides
from zope.interface import implementer
from zope.interface import implementsOnly
from plone.app.z3cform.interfaces import IRelatedItemsWidget
from plone.app.z3cform.widget import RelatedItemsWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import alsoProvides
from plone.app.dexterity.behaviors.nextprevious import INextPreviousEnabled
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from plone.namedfile.utils import safe_basename

from plone.app.content.utils import json_dumps
from plone.app.content.utils import json_loads

from plone import api
from plone import namedfile

from zope.interface import Interface
from zope import schema
from z3c.form import form
from z3c.form import field

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

def possibleBasemaps(context):
    path = '/'.join(context.getPhysicalPath()
                    [:2]) + '/resources/basemaps'
    return CatalogSource(
        path={'query': '/data/villages'},
        portal_type=('Organization', 'Building')
    )
directlyProvides(possibleBasemaps, IContextSourceBinder)

class INewHouseWizard(Interface):
    """ Define form fields """

    title = schema.TextLine(
        title=_(u'Title'),
    )

    village = RelationChoice(
        title=_(u'label_mapfile_basemap', default=u'Village'),
        source=possibleBasemaps,
        required=False
    )

    location = schema.TextLine(
        title=_(u'Location'),
        required=False
    )

class NewHouseWizardForm(form.Form):

    label = _(u'New House Wizard')
    fields = field.Fields(INewHouseWizard)
    ignoreContext = True

    @button.buttonAndHandler(_('Import'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        resource = data['resource']
        container = aq_inner(self.context)
        # set success pattern includes new map url
        self.status = _(u'Import resource operation successfully')

    @button.buttonAndHandler(_(u'Cancel'))
    def handleCancel(self, action):
        self.status = _(u'Import resource operation cancelled')
        notify(AddCancelledEvent(self.context))

class NewHouseWizard(BrowserView):

    index = ViewPageTemplateFile("new_house_wizard.pt")

    def __call__(self):
        return self.index()

class ImportHouseView(BrowserView):
    """导入SweetHome3D生成的房屋结构图，是一个压缩文件，内容如下

    config.json
    views/
        plan/house.jpg
        solid/house.jpg
        three/house.mtl

    其中 config.json 包含下列配置信息


    endpoint: fileUpload
        plone.app.content-3.0.20-py2.7.egg/plone/app/content/browser/file.py

    """
    def __call__(self):
        container = api.content.get(path=self.request.form['form.widgets.building'])
        title = self.request.form['form.widgets.title']
        geolocation = self.request.form['form.widgets.location']
        data = self.request.form['form.widgets.file']
        house = self.import_entry_from_zip(container, title, geolocation, data)
        return json_dumps({ 
            'name': house.getId(),
            'url': house.absolute_url(),
        })

    def get_file_data(self, value):
        # plone.formwidget.namedfile-1.0.15-py2.7.egg/plone/formwidget/namedfile/converter.py
        filename = safe_basename(value.filename)
        if filename is not None and not isinstance(filename, unicode):
            # Work-around for
            # https://bugs.launchpad.net/zope2/+bug/499696
            filename = filename.decode('utf-8')

        value.seek(0)
        data = value.read()
        return data

    def import_entry_from_zip(self, container, title, geolocation, data):
        f = ZipFile(data, 'r')
        config = json_loads(f.read('config.json'))
        house = api.content.create(
            type='House',
            container=container,
            geolocation=geolocation,
            geometry=config['geometry'],
            title=title,
            safe_id=True)

        entries = {}
        for x in f.namelist():
            if x.startswith('views/'):
                if x[-1] == '/':
                    k = x.split('/')[-2]
                    entries[k] = []
                else:
                    k = x.split('/')[-2]
                    entries[k].append(x)

        for view in config.get('views', []):
            view_type = view['type']
            house_view = api.content.create(
                type='HouseView',
                container=house,
                view_type=view_type,
                geolocation=geolocation,
                geometry=view['geometry'],
                title=view_type,
                safe_id=True)
            for x in entries.get(view_type, []):
                result = self.import_file(house_view, os.path.basename(x), f.read(x))

        return house

    def import_file(self, container, filename, filedata):
        content_type = mimetypes.guess_type(filename)[0] or ""

        # ctr = getToolByName(self.context, 'content_type_registry')
        # type_ = ctr.findTypeName(filename.lower(), '', '') or 'File'
        # # Now check that the object is not restricted to be added in the
        # # current context
        # allowed_ids = [
        #     fti.getId() for fti in container.allowedContentTypes()
        # ]
        # if type_ not in allowed_ids:
        #     pass

        factory = IDXFileFactory(container)
        obj = factory(filename, content_type, filedata)

        result = {
            "type": '',
            "size": 0
        }

        if 'File' in obj.portal_type:
            result['size'] = obj.file.getSize()
            result['type'] = obj.file.contentType
        elif 'Image' in obj.portal_type:
            result['size'] = obj.image.getSize()
            result['type'] = obj.image.contentType

        result.update({
            'url': obj.absolute_url(),
            'name': obj.getId(),
            'UID': IUUID(obj),
            'filename': filename
        })
        return json_dumps(result)

class HouseFeatureEditor(BrowserView):

    index = ViewPageTemplateFile("house_feature_editor.pt")

    def __call__(self):
        return super(HouseFeatureEditor, self).__call__()
