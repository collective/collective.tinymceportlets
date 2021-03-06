from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app.component.hooks import getSite
from zope.component import getUtilitiesFor, getUtility, \
    getMultiAdapter
from plone.portlets.interfaces import IPortletManager, IPortletRetriever
from Products.CMFCore.utils import getToolByName
from collective.tinymceportlets.utils import portletHash

_pm_titles = {
    'plone.leftcolumn': 'Left Column',
    'plone.rightcolumn': 'Right Column',
    'collective.tinymceportlets': 'Tiny MCE Portlets'
}


def Portlets(context):
    site = getSite()

    try:
        req = site.REQUEST
    except AttributeError:
        req = context.REQUEST

    if 'manager' not in req:
        utils = getUtilitiesFor(IPortletManager)
        mng_name = [(n, m) for n, m in utils if 'dashboard' not in n][0][0]
    else:
        mng_name = req.get('manager')

    if 'context' in req:
        context_req = str(req.get('context')).strip()
        mod_context = context.restrictedTraverse(context_req, None)
        if mod_context is None:
            ref_cat = getToolByName(site, 'reference_catalog')
            mod_context = ref_cat.lookupObject(context_req)
        if mod_context:
            context = mod_context

    terms = []
    utils = getUtilitiesFor(IPortletManager)
    for mng_name, pm in [(n, m) for n, m in utils if 'dashboard' not in n]:
        title = _pm_titles.get(mng_name, mng_name)
        manager = getUtility(IPortletManager, name=mng_name, context=context)
        retriever = getMultiAdapter((context, manager), IPortletRetriever)
        for portlet in retriever.getPortlets():
            assignment = portlet['assignment']
            name = '%s - %s' % (title, assignment.__name__)
            value = portletHash(manager, assignment, context)
            terms.append(SimpleTerm(value=value, token=value, title=name))

    return SimpleVocabulary(terms)
