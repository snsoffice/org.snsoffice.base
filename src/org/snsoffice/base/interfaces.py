# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from org.snsoffice.base import _

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope import schema
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

PhaseTypeVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'image/*', title=_(u'Photo')),
     SimpleTerm(value=u'panorama/equirectangular', title=_(u'Panorama Equirectangular')),
     SimpleTerm(value=u'panorama/cubemap', title=_(u'Panorama Cube')),
     SimpleTerm(value=u'text/html', title=_(u'Text')),
     SimpleTerm(value=u'video/*', title=_(u'Video'))]
)

HouseViewVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'plan', title=_(u'Plan')),
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

class IOrgSnsofficeBaseLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ISpot(model.Schema):
    """Schema for Spot content type."""

    anchors = schema.Tuple(
        title=_(u'label_anchors', u'Anchors'),
        description=_(
            u'help_anchors',
            default=u"Persons responsible for living this house."
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )

    directives.widget(
        'anchors',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Users'
    )

    source = schema.URI(
        title=_(u'label_spot_source', default=u'Source'),
        description=_(u"External url of this spot"),
        required=False,
    )


class IOrganization(ISpot):
    """Schema for Organization content type."""

    org_type = schema.Choice(
        title=_(u'Type'),
        vocabulary=OrganizationVocabulary,
        required=True
    )

class IVillage(IOrganization):
    """Schema for Village content type."""

class IHotel(IOrganization):
    """Schema for Hotel content type."""

class ISchool(IOrganization):
    """Schema for School content type."""

class IStation(IOrganization):
    """Schema for Station content type."""

class IAirport(IOrganization):
    """Schema for Station content type."""

class IPark(IOrganization):
    """Schema for Park content type."""

class IHouse(ISpot):
    """Schema for House content type."""

class IBuilding(IHouse):
    """Schema for Building content type."""

class IFloor(IHouse):
    """Schema for Floor content type."""

class IRoom(IHouse):
    """Schema for Room content type."""

class IHouseView(model.Schema):
    """Schema for HouseView content type."""

    fieldset(_(u'View'), fields=['view_type', 'source', 'opacity'])

    view_type = schema.Choice(
        title=_(u'Type'),
        vocabulary=HouseViewVocabulary,
        required=True
    )

    source = schema.URI(
        title=_(u'label_view_source', default=u'Source'),
        description=_(u"External resource of this view"),
        required=False,
    )

    opacity = schema.Float(
        title=_(u'label_opacity', default=u'Opacity'),
        required=False,
    )


class IPlanView(IHouseView):
    """Schema for PlanView content type."""

class ISolidView(IHouseView):
    """Schema for SolidView content type."""

class IThreeView(IHouseView):
    """Schema for ThreeView content type."""

class IPhase(model.Schema):
    """Schema for Phase content type."""

    phase_type = schema.Choice(
        title=_(u'Type'),
        vocabulary=PhaseTypeVocabulary,
        required=True
    )

    source = schema.URI(
        title=_(u'label_phase_source', default=u'Source'),
        description=_(u"External url of this phase"),
        required=False,
    )

class IHouseFeature(IPhase):
    """Schema for HouseFeature content type."""

class IScene(model.Schema):
    """Schema for Scene content type."""
