# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from plone.indexer import indexer
from org.snsoffice.base.interfaces import IHouse

@indexer(IHouse)
def getHouseVillage(object):
    if hasattr(object, 'building'):
        return object.building.to_object.__parent__.title_or_id()
