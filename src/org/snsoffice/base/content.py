# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from plone.dexterity.content import Container
from plone.dexterity.content import Item
from zope.interface import implementer
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.content import Folder
from plone.app.content.utils import json_loads
from zope.component import getAdapter
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict


class Organization(Container):
    """Class for Organization"""
    pass

class House(Container):
    """Class for House"""

    def getHouseLocation(self):        
        locations = []
        obj = self.context.__parent__
        while True:
            locations.append(obj.title_or_id())
            obj = obj.__parent__
            if IOrganization.providedBy(obj):
                break
        locations.reverse()
        return ' - '.join(locations)

class Building(House):
    """Class for Building"""
    pass
    
class Floor(House):
    """Class for Floor"""
    pass

class Room(House):
    """Class for Room"""
    pass

class HouseView(Container):
    """Class for HouseView"""
    pass

class HouseFeature(Container):
    """Class for HouseFeature"""
    pass
