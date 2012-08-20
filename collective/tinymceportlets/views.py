from plone.portlets.interfaces import ILocalPortletAssignmentManager
from Acquisition import aq_inner
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.portlets.constants import CONTEXT_CATEGORY
from zope.component import getUtility
from plone.portlets.constants import GROUP_CATEGORY
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from zope.component import adapts
from zope.interface import Interface, implements
from zope.schema import Choice
from plone.formwidget.contenttree import ContentTreeFieldWidget
from plone.formwidget.contenttree import PathSourceBinder
from z3c.form import form, button, field
from zope.app.pagetemplate import ViewPageTemplateFile as Zope3PageTemplateFile
from plone.app.portlets.browser.manage import ManageContextualPortlets


class IPortletSelectionForm(Interface):

    context = Choice(
        title=u"Content Item",
        source=PathSourceBinder()
    )

    portlet = Choice(
        title=u"Portlet",
        vocabulary="collective.tinymceportlets.vocabularies.contextportlets"
    )


class PortletSelectionAdapter(object):
    implements(IPortletSelectionForm)
    adapts(Interface)

    manager = ''
    context = ''
    portlet = ''

    def __init__(self, context):
        self.context = context


class PortletSelectionForm(form.Form):
    template = Zope3PageTemplateFile("templates/portlets-selection.pt")
    fields = field.Fields(IPortletSelectionForm)
    fields['context'].widgetFactory = ContentTreeFieldWidget

    @button.buttonAndHandler(u'Save')
    def handle_save(self, action):
        pass

    @button.buttonAndHandler(u'Cancel')
    def handle_cancel(self, action):
        pass

    @button.buttonAndHandler(u'Remove')
    def handle_remove(self, action):
        pass


PortletSelectionFormView = PortletSelectionForm


class TinyMCEPortletsManager(ManageContextualPortlets):

    def __init__(self, context, request):
        super(TinyMCEPortletsManager, self).__init__(context, request)

    def __call__(self):
        portletManager = getUtility(IPortletManager,
                                    name='collective.tinymceportlets')
        assignable = getMultiAdapter((self.context, portletManager),
                                     ILocalPortletAssignmentManager)
        assignments = getMultiAdapter((self.context, portletManager),
                                      IPortletAssignmentMapping)

        IPortletPermissionChecker(assignments.__of__(aq_inner(self.context)))()

        if not assignable.getBlacklistStatus(GROUP_CATEGORY):
            assignable.setBlacklistStatus(GROUP_CATEGORY, True)
        if not assignable.getBlacklistStatus(CONTENT_TYPE_CATEGORY):
            assignable.setBlacklistStatus(CONTENT_TYPE_CATEGORY, True)
        if not assignable.getBlacklistStatus(CONTEXT_CATEGORY):
            assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)
        return super(TinyMCEPortletsManager, self).__call__()
