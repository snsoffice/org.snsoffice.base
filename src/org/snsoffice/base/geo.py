# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives as form
from plone.supermodel import model
from zope.interface import provider
from z3c.form.interfaces import IFieldWidget, INPUT_MODE, DISPLAY_MODE, HIDDEN_MODE
from zope import schema
from z3c.form.browser.text import TextWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

class GeoFieldWidget(TextWidget):
    """Geo feature input field.

    <tal:def define="context            nocall:view/form/context;
                     portal_url         nocall:context/portal_url;">
      <script type="text/javascript" src=""
              tal:attributes="src string:${portal_url}/++resource++geohelper.js;" />
    </tal:def>
    """
    input_template = ViewPageTemplateFile("browser/text_input.pt")

    def render(self):
        """See z3c.form.interfaces.IWidget."""

        if self.mode == INPUT_MODE:
            self.template = self.input_template

        return TextWidget.render(self)

@provider(IFormFieldProvider)
class IGeoFeature(model.Schema):
    """GeoFeature interface to store geometry and style of feature.
    """

    model.fieldset(
        'geofeature',
        label=_(u"label_tab_geofeture", default=u'Geography'),
        fields=['coordinate']
    )

    coordinate = schema.TextLine(
        title=_(u'label_coordinate', default=u'Coordinate'),
        description=_(u"Location of this spot in projection ESPG:3857"),
        required=False,
    )

    form.widget(
        'coordinate',
        GeoFieldWidget
    )
