"""

    Simple sample form

"""

from plone.directives import form

from zope import schema
from z3c.form import button

from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage

class IImportForm(form.Schema):
    """ Define form fields """

    name = schema.TextLine(
            title=u"Your name",
        )

class ImportForm(form.SchemaForm):
    """ Define Form handling

    This form can be accessed as http://yoursite/@@importer

    """

    schema = IImportForm
    ignoreContext = True

    label = u"Importer"
    description = u"Import house view from SweetHome3D"

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do something with valid data here

        # Set status on this form page
        # (this status message is not bind to the session and does not go thru redirects)
        self.status = "Thank you very much!"

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
