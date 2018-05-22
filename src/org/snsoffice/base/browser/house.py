# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from io import BytesIO
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
    
    """
    def __call__(self):        
        container = api.content.get(path=self.request.form['form.widgets.building'])
        title = self.request.form['form.widgets.title']
        geolocation = self.request.form['form.widgets.geolocation']
        data = self.request.form['form.widgets.file']
        house = import_entry_from_zip(self, container, title, geolocation, data)        
        return json_dumps({ 'id': house.getId() })
    
    def import_entry_from_zip(self, container, title, geolocation, data):
        f = ZipFile(BytesIO(data), 'r')
        config = json_loads(f.read('config.json'))
        namelist = f.namelist()
        house = api.content.create(
            type='House',
            container=container,
            geolocation=geolocation,
            title=title,
            safe_id=True)
        return house

class HouseFeatureEditor(BrowserView):

    index = ViewPageTemplateFile("house_feature_editor.pt")

    def __call__(self):
        return super(HouseFeatureEditor, self).__call__()
