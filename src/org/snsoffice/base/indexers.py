# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from plone.indexer import indexer
from org.snsoffice.base.interfaces import IHouse

@indexer(IHouse)
def getHouseVillage(object):
    return object.__parent__.__parent__.title_or_id()
