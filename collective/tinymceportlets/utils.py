from collective.tinymceportlets import PORTLET_CLASS_IDENTIFIER


def portletHash(manager, assignment, context):
    if hasattr(context, 'UID'):
        context = context.UID()
    else:
        context = '/'.join(context.getPhysicalPath())
    return "%s-%s-%s" % (
        manager.__name__,
        assignment.__name__,
        context
    )


def portletMarkup(hash):
    return \
"""<img class="%s mce-only %s"
        src="++resource++collective.tinymceportlets/add-portlets.png"/>""" % (
            PORTLET_CLASS_IDENTIFIER, hash)


def decodeHash(hash):
    first, rest = hash.split('-', 1)
    result = [first]
    result.extend(rest.rsplit('-', 1))
    return result
