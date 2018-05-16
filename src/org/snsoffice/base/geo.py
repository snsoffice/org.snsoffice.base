# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives as form
from plone.supermodel import model
from zope.interface import provider
from zope import schema

@provider(IFormFieldProvider)
class IGeoFeature(model.Schema):
    """GeoFeature interface to store geometry and style of feature.
    """

    model.fieldset(
        'geofeature',
        label=_(u"label_tab_geofeture", default=u'Geography'),
        fields=['geolocation', 'geostyle', 'geoextent', 'geoangle']
    )

    geolocation = schema.TextLine(
        title=_(u'label_geolocation', default=u'Location'),
        description=_(u"Location of this spot in projection ESPG:3857"),
        required=False,
    )

    # geometry = schema.TextLine(
    #     title=_(u'label_geometry', default=u'Geometry'),
    #     description=_(u"Feature geometry in WKT format"),
    #     required=False,
    # )

    geostyle = schema.TextLine(
        title=_(u'label_geostyle', default=u'Style'),
        description=_(u"Feature style in JSON format"),
        required=False,
    )

    geoextent = schema.TextLine(
        title=_(u'label_geoextent', default=u'Extent'),
        description=_(u"Extent of the building or image"),
        required=False,
    )

    geoangle = schema.TextLine(
        title=_(u'label_angel', default=u'Angle'),
        description=_(u"North in degree"),
        required=False,
    )
