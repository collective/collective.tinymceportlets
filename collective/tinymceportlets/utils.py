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
"""<img class="%s mce-only %s"
        src="++resource++collective.tinymceportlets/add-portlets.png"/>""" % (
            PORTLET_CLASS_IDENTIFIER, hash)


def decodeHash(hash):
    mng, assignment, context = hash.split('-')
    return decode(mng), decode(assignment), decode(context)
