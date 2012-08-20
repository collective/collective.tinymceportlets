from lxml import etree
from lxml.cssselect import CSSSelector
from lxml.html import fromstring

from repoze.xmliter.utils import getHTMLSerializer

from zope.interface import implements, Interface
from zope.component import adapts
from zope.site.hooks import getSite

from collective.tinymceportlets.interfaces import TinyMCEPortletsLayer
from collective.tinymceportlets import PORTLET_CLASS_IDENTIFIER
from collective.tinymceportlets.utils import renderPortletFromHash

from plone.transformchain.interfaces import ITransform
from Products.CMFCore.utils import getToolByName

_portlet_selector = CSSSelector('div.' + PORTLET_CLASS_IDENTIFIER)


def add_portlet(tag, request, site, ref_cat, view):
    klass = tag.attrib.get('class', '').\
                replace(PORTLET_CLASS_IDENTIFIER, '').\
                replace('mce-only ', '').\
                replace('mceNonEditable', '').strip()
    tag.attrib['class'] = tag.attrib.get('class', '').replace('mce-only ', '')
    try:
        html = renderPortletFromHash(klass, request, site=site,
            ref_cat=ref_cat, view=view)
    except:
        html = None
    if html is None:
        tag.getparent().remove(tag)
        return

    style = tag.attrib.get('style', '')
    if style:
        style = style.strip().strip(';') + ';'
    if 'width' in tag.attrib:
        style += 'width:%spx;' % tag.attrib['width'].strip('px')
    if 'height' in tag.attrib:
        style += 'height:%spx;' % tag.attrib['height'].strip('px')
    html = '<div class="tinymceportlet" style="%s">%s</div>' % (
        style, html
    )
    tag.addnext(fromstring(html))
    tag.getparent().remove(tag)


class TinyMCEPortletsTransform(object):
    implements(ITransform)
    adapts(Interface, TinyMCEPortletsLayer)
    # rather early off so other things, like xdv/diazo can leverage it
    order = 8100

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transformString(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformUnicode(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformIterable(self, result, encoding):
        contentType = self.request.response.getHeader('Content-Type')
        if contentType is None or not contentType.startswith('text/html'):
            return None

        ce = self.request.response.getHeader('Content-Encoding')
        if ce and ce in ('zip', 'deflate', 'compress'):
            return None
        try:
            result = getHTMLSerializer(result, pretty_print=False)
        except (TypeError, etree.ParseError):
            return None

        portlets = _portlet_selector(result.tree)
        if len(portlets) > 0:
            site = getSite()
            ref_cat = getToolByName(site, 'reference_catalog')
            view = site.restrictedTraverse('@@plone')
            for tag in portlets:
                add_portlet(tag, self.request, site, ref_cat, view)

        return result
