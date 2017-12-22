# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.supermodel import model

class IOrgSnsofficeBaseLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IHouse(model.Schema):
    """Schema for House content type."""
    
    anchor = schema.TextLine(title=_(u'Username of the anchor'))
    source = schema.URL(title=_(u'Source uri of this house'))

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
