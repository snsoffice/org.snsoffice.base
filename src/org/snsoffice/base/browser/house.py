# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from Acquisition import aq_inner
from zope.component import getAdapter
from Products.Five import BrowserView
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

from plone import api
from plone import namedfile

from zope.interface import Interface
from zope import schema
from z3c.form import form
from z3c.form import field

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

class INewHouseWizard(Interface):
    """ Define form fields """

    title = schema.TextLine(
        title=_(u'Title'),
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False
    )

    # basemap = schema.Choice(
    #     title=_(u'Base map'),
    #     required=False,
    #     missing_value='',
    #     vocabulary=basemap_vocab
    # )
    basemap = RelationChoice(
        title=_(u'label_mapfile_basemap', default=u'Base map'),
        source=possibleBasemaps,
        required=False
    )


class NewMapForm(form.Form):

    fields = field.Fields(IMapFormSchema)
    ignoreContext = True

    def __init__(self, context, request):
        super(NewMapForm, self).__init__(context, request)

    def updateFields(self):
        super(NewMapForm, self).updateFields()

    def updateWidgets(self):
        self.fields['basemap'].widgetFactory = BasemapFieldWidget
        super(NewMapForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        title = data['title']
        description = data['description']
        basemap = data['basemap']

        container = aq_inner(self.context)
        map = api.content.create(
            type='map_file',
            container=container,
            title=title,
            description=description,
            safe_id=True)

        if map:
            alsoProvides(map, INextPreviousEnabled)
            # Copy basemap
            if basemap:
                image = basemap
                newobj = api.content.copy(source=basemap, target=map)
                # Change ownership of newobj
                user = map.getOwner()
                newobj.changeOwnership(user, recursive=False)
                newobj.manage_setLocalRoles(user.getId(), ["Owner", ])
                newobj.reindexObjectSecurity()
            else:
                image = api.content.get(
                    path='/resources/basemaps/empty')

            # Copy image
            map.image = namedfile.NamedBlobImage(
                image.image.data, filename=unicode(basemap))

            # set success pattern includes new map url
            self.status = '{SNSGIS_NEW_MAP_OBJECT_URL:%s}' % map.absolute_url()

    @button.buttonAndHandler(_(u'Cancel'))
    def handleCancel(self, action):
        self.status = _(u'Add map operation cancelled')
        notify(AddCancelledEvent(self.context))


class NewHouseWizard(BrowserView):

    def __call__(self):
        return super(NewHouseWizard, self).__call__()

class ImportHouseView(BrowserView):

    def __call__(self):
        return super(ImportHouseView, self).__call__()

class HouseFeatureEditor(BrowserView):

    def __call__(self):
        return super(HouseFeatureEditor, self).__call__()


class NewHouseFeature(BrowserView):

    def __call__(self):
        return super(NewHouseFeature, self).__call__()

class EditHouseFeature(BrowserView):

    def __call__(self):
        return super(EditHouseFeature, self).__call__()

