# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from org.snsoffice.base import _

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope import schema
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives
from plone.supermodel import model

class IOrgSnsofficeBaseLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IHouse(model.Schema):
    """Schema for House content type."""
    
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
        title=_(u'label_house_source', default=u'Source'),
        description=_(u"External url of this house resource"),
        required=False,
    )

class IOrganization(IHouse):
    """Schema for Organization content type."""

class IBuilding(IHouse):
    """Schema for Building content type."""

class IFloor(IHouse):
    """Schema for Floor content type."""

class IRoom(IHouse):
    """Schema for Room content type."""
