# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from org.snsoffice.base import _

from plone import api
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope import schema
from zope.interface import Interface
from zope.interface import provider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from z3c.form.interfaces import IEditForm
from z3c.relationfield.schema import RelationChoice

PUBLIC_DOMAIN = u'Public'
PUBLIC_DOMAIN_TITLE = _(u'label_public_domain', default=u'Public')

HOUSE_DOMAIN_PARAMETER = 'houseDomain'

HouseDomainVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'public', title=_(u'Public'))]
)

PhaseTypeVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'photo', title=_(u'Photo')),
     SimpleTerm(value=u'panorama', title=_(u'Panorama Equirectangular')),
     SimpleTerm(value=u'page', title=_(u'Text')),
     SimpleTerm(value=u'video5', title=_(u'Video'))]
)

HouseViewVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'plane', title=_(u'Plan')),
     SimpleTerm(value=u'solid', title=_(u'Solid')),
     SimpleTerm(value=u'three', title=_(u'3D Model'))]
)

OrganizationVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'village', title=_(u'Village')),
     SimpleTerm(value=u'hotel', title=_(u'Hotel')),
     SimpleTerm(value=u'school', title=_(u'School')),
     SimpleTerm(value=u'park', title=_(u'Park')),
     SimpleTerm(value=u'station', title=_(u'Station')),
     SimpleTerm(value=u'airport', title=_(u'Airport'))]
)

@provider(IContextSourceBinder)
def domains_source(context):
    user = api.user.get_current()
    roles = api.user.get_roles(user=user)
    return SimpleVocabulary([
        SimpleTerm(value=u'public', title=_(u'Public'))
    ]) if 'Manager' in roles else SimpleVocabulary([])

class IOrgSnsofficeBaseLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ISpot(model.Schema):
    """Schema for Spot content type."""

    # anchors = schema.Tuple(
    #     title=_(u'label_anchors', u'Anchors'),
    #     description=_(
    #         u'help_anchors',
    #         default=u"Persons responsible for living this house."
    #     ),
    #     value_type=schema.TextLine(),
    #     required=False
    # )

    # directives.widget(
    #     'anchors',
    #     AjaxSelectFieldWidget,
    #     vocabulary='plone.app.vocabularies.Users'
    # )

    geometry = schema.TextLine(
        title=_(u'label_geometry', default=u'Geometry'),
        description=_(u"Building geometry in WKT format"),
        required=False,
    )

    geostyle = schema.TextLine(
        title=_(u'label_geostyle', default=u'Style'),
        description=_(u"Building style in JSON format"),
        required=False,
    )

    model.fieldset(
        'geofeature',
        label=_(u"label_tab_geofeture", default=u'Geography'),
        fields=['geometry', 'geostyle']
    )

class IOrganization(ISpot):
    """Schema for Organization content type."""

    org_type = schema.Choice(
        title=_(u"label_org_type", default=u'Type'),
        vocabulary=OrganizationVocabulary,
        required=True
    )

class IHouse(ISpot):
    """Schema for House content type."""

    building = RelationChoice(
        title=_(u'Building'),
        required=True,
        source=CatalogSource(path='/future/data/villages', portal_type=('Building',)),
    )

    house_type = schema.TextLine(
        title=_(u'label_house_type', default=u'House Type'),
        description=_(u"House type"),
        required=False,
    )

    floor = schema.Int(
        title=_(u'label_house_floor', default=u'Floor'),
        description=_(u"House floor"),
        required=False,
    )

    area = schema.Float(
        title=_(u'label_house_area', default=u'Area'),
        description=_(u"House area (square meters)"),
        required=False,
    )

    model.fieldset(
        'house',
        label=_(u"label_tab_house", default=u'House'),
        fields=['building', 'house_type', 'floor', 'area']
    )

class IBuilding(ISpot):
    """Schema for Building content type."""

class IFloor(ISpot):
    """Schema for Floor content type."""

class IRoom(IHouse):
    """Schema for Room content type."""

class IHouseView(model.Schema):
    """Schema for HouseView content type."""

    view_type = schema.Choice(
        title=_(u'Type'),
        vocabulary=HouseViewVocabulary,
        required=True
    )

    geometry = schema.TextLine(
        title=_(u'label_geometry', default=u'Geometry'),
        description=_(u"View boundary"),
        required=False,
    )

    # geoextent = schema.TextLine(
    #     title=_(u'label_geoextent', default=u'Extent'),
    #     description=_(u"Extent of the view"),
    #     required=False,
    # )

    opacity = schema.Float(
        title=_(u'label_opacity', default=u'Opacity'),
        default=1.0,
        required=False,
    )

    source = schema.TextLine(
        title=_(u'label_view_source', default=u'Source'),
        description=_(u"Resource of this view"),
        required=False,
    )

    model.fieldset(
        'geofeature',
        label=_(u"label_tab_geofeture", default=u'Geography'),
        fields=['geometry']
    )

class IPhase(model.Schema):
    """Schema for Phase content type."""

    phase_type = schema.Choice(
        title=_(u'label_phase_type', default=u'Type'),
        vocabulary=PhaseTypeVocabulary,
        required=True
    )

    source = schema.TextLine(
        title=_(u'label_phase_source', default=u'Source'),
        description=_(u"Resource of this phase"),
        required=False,
    )

    model.fieldset(
        'geofeature',
        label=_(u"label_tab_geofeture", default=u'Geography'),
        fields=['geoangle']
    )

    geoangle = schema.Float(
        title=_(u'label_angel', default=u'Angle'),
        description=_(u"North in degree"),
        default=0.,
        min=0.,
        max=360.,
        required=False,
    )

class IHouseFeature(IPhase):
    """Schema for HouseFeature content type."""

class IScene(model.Schema):
    """Schema for Scene content type."""

class IPublicHouse(Interface):
    """Only house marked with interface will be accessed in public space"""
