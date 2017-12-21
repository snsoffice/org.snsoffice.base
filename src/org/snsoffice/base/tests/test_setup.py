# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from org.snsoffice.base.testing import ORG_SNSOFFICE_BASE_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that org.snsoffice.base is properly installed."""

    layer = ORG_SNSOFFICE_BASE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if org.snsoffice.base is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'org.snsoffice.base'))

    def test_browserlayer(self):
        """Test that IOrgSnsofficeBaseLayer is registered."""
        from org.snsoffice.base.interfaces import (
            IOrgSnsofficeBaseLayer)
        from plone.browserlayer import utils
        self.assertIn(IOrgSnsofficeBaseLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ORG_SNSOFFICE_BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['org.snsoffice.base'])

    def test_product_uninstalled(self):
        """Test if org.snsoffice.base is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'org.snsoffice.base'))

    def test_browserlayer_removed(self):
        """Test that IOrgSnsofficeBaseLayer is removed."""
        from org.snsoffice.base.interfaces import IOrgSnsofficeBaseLayer
        from plone.browserlayer import utils
        self.assertNotIn(IOrgSnsofficeBaseLayer, utils.registered_layers())
