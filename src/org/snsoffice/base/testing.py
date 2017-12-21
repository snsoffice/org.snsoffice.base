# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import org.snsoffice.base


class OrgSnsofficeBaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=org.snsoffice.base)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'org.snsoffice.base:default')


ORG_SNSOFFICE_BASE_FIXTURE = OrgSnsofficeBaseLayer()


ORG_SNSOFFICE_BASE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ORG_SNSOFFICE_BASE_FIXTURE,),
    name='OrgSnsofficeBaseLayer:IntegrationTesting'
)


ORG_SNSOFFICE_BASE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ORG_SNSOFFICE_BASE_FIXTURE,),
    name='OrgSnsofficeBaseLayer:FunctionalTesting'
)


ORG_SNSOFFICE_BASE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        ORG_SNSOFFICE_BASE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='OrgSnsofficeBaseLayer:AcceptanceTesting'
)
