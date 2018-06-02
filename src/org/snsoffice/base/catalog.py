# -*- coding: utf-8 -*-
from binascii import b2a_qp
from plone import api
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.querystring import queryparser
from plone.app.vocabularies import SlicableVocabulary
from plone.app.vocabularies.terms import BrowsableTerm
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ZCTextIndex.ParseTree import ParseError
from zope.browser.interfaces import ITerms
from zope.formlib.interfaces import ISourceQueryView
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import ISource
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite

from org.snsoffice.base.interfaces import IHouse

@implementer(IVocabularyFactory)
class KeywordsVocabulary(object):
    """Vocabulary factory listing all catalog keywords from the "Subject"
    index. Add default keyword IHouse.PUBLIC_DOMAIN for Manager."""

    # KeywordVocabularies for other keyword indexes
    keyword_index = 'Subject'

    def __call__(self, context, query=None):
        site = getSite()
        self.catalog = getToolByName(site, "portal_catalog", None)
        if self.catalog is None:
            return  SimpleVocabulary([])
        index = self.catalog._catalog.getIndex(self.keyword_index)

        def safe_encode(term):
            if isinstance(term, unicode):
                # no need to use portal encoding for transitional encoding from
                # unicode to ascii. utf-8 should be fine.
                term = term.encode('utf-8')
            return term
        # Vocabulary term tokens *must* be 7 bit values, titles *must* be
        # unicode
        items = [
            SimpleTerm(i, b2a_qp(safe_encode(i)), safe_unicode(i))
            for i in index._index
            if (query is None or safe_encode(query) in safe_encode(i)) \
            and i != IHouse.PUBLIC_DOMAIN
        ]
        user = api.user.get_current()
        if 'Manager' in api.user.get_roles(user=user):
            i = IHouse.PUBLIC_DOMAIN
            items.append(SimpleTerm(i, b2a_qp(safe_encode(i)),
                                    IHouse.PUBLIC_DOMAIN_TITLE))
        return SimpleVocabulary(items)

KeywordsVocabularyFactory = KeywordsVocabulary()
