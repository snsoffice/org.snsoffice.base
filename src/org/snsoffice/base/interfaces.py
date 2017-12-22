# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from org.snsoffice.base import _

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.supermodel import model
from zope import schema

class IOrgSnsofficeBaseLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IHouse(model.Schema):
    """Schema for House content type."""
    
    anchor = schema.TextLine(
        title=_(u'label_house_anchor', defalut=u'Username of the anchor'),
        description=_(u"Anchor for this house"),
        required=False,

    )
    source = schema.URI(
        title=_(u'label_house_source', default=u'Source uri of this house'),
        description=_(u"External url of house resource"),
        required=False,
    )

    # def getAnchor():
    # """Get anchor of this house, None if no available anchor."""

class IOrganization(IHouse):
    """Schema for Organization content type."""

class IBuilding(IHouse):
    """Schema for Building content type."""

class IFloor(IHouse):
    """Schema for Floor content type."""

class IRoom(IHouse):
    """Schema for Room content type."""
