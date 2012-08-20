from zope.app.component.hooks import getSite
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletRenderer
from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from zope.component import queryMultiAdapter
from Products.CMFCore.utils import getToolByName
from collective.tinymceportlets import PORTLET_CLASS_IDENTIFIER
import binascii
decode = binascii.a2b_hex
encode = binascii.b2a_hex


def portletHash(manager, assignment, context):
    if hasattr(context, 'UID'):
        context = context.UID()
    else:
        context = '/'.join(context.getPhysicalPath())
    return "%s-%s-%s" % (
        encode(manager.__name__),
        encode(assignment.__name__),
        encode(context)
    )


def portletMarkup(hash):
    return \
"""<div class="%s mce-only %s mceNonEditable">%s</div>""" % (
            PORTLET_CLASS_IDENTIFIER, hash, ''
            )


def decodeHash(hash):
    mng, assignment, context = hash.split('-')
    return decode(mng), decode(assignment), decode(context)


def renderPortletFromHash(hash, request, site=None, ref_cat=None, view=None):
    if site is None:
        site = getSite()
    if ref_cat is None:
        ref_cat = getToolByName(site, 'reference_catalog')
    if view is None:
        view = site.restrictedTraverse('@@plone')

    manager, portletname, uid = decodeHash(hash)
    # get uid if object supports that.
    context = ref_cat.lookupObject(uid)
    if not context:  # try traversing to it next
        context = site.restrictedTraverse(uid, None)
        if not context:  # if not found, skip over it..
            return None
    manager = getUtility(IPortletManager, name=manager, context=context)
    assignments = getMultiAdapter((context, manager),
        IPortletAssignmentMapping)
    if portletname in assignments:
        portlet = assignments[portletname]
    else:
        return None
    renderer = queryMultiAdapter((context, request, view, manager, portlet),
                                 IPortletRenderer)
    if not renderer:
        return None

    # Make sure we have working acquisition chain
    renderer = renderer.__of__(context)

    if not renderer:
        return None

    renderer.update()
    return renderer.render()
