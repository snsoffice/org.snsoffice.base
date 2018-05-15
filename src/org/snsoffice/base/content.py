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

class Organization(Folder):
    """Class for Organization"""
    pass

class House(Folder):
    """Class for House"""
    pass

class Building(House):
    """Class for Building"""

    def getGeoJson(self):
        pass

class Floor(House):
    """Class for Floor"""

    def getGeoJson(self):
        pass

class Room(House):
    """Class for Room"""

    def getGeoJson(self):
        pass

class HouseView(Item):
    """Class for HouseView"""

    def getGeoJson(self):
        pass

class HouseFeature(Item):
    """Class for HouseFeature"""

    def getGeoJson(self):
        pass


