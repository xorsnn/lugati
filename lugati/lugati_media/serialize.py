# encoding: utf-8
import mimetypes
import re
from django.core.urlresolvers import reverse
from sorl.thumbnail import get_thumbnail

def order_name(name):
    """order_name -- Limit a text to 20 chars length, if necessary strips the
    middle of the text and substitute it for an ellipsis.

    name -- text to be limited.

    """
    name = re.sub(r'^.*/', '', name)
    if len(name) <= 20:
        return name
    return name[:10] + "..." + name[-7:]


def serialize(instance, file_attr='file'):
    """serialize -- Serialize a Picture instance into a dict.

    instance -- Picture instance
    file_attr -- attribute name that contains the FileField or ImageField

    """
    obj = getattr(instance, file_attr)
    return {
        'url': obj.url,
        'name': order_name(obj.name),
        'type': mimetypes.guess_type(obj.path)[0] or 'image/png',
        'thumbnailUrl': str(get_thumbnail(instance.file, '100x100', crop='center', quality=100).url),
        'size': obj.size,
        'deleteUrl': reverse('lugati_media:lugati_remove_image', args=[instance.pk]),
        'deleteType': 'DELETE',
        #'image_url' : unicode(self.object.get_url()),
        'pic_id'    : str(instance.id),
        'preview_url': str(get_thumbnail(instance.file, '400x400', crop='center', quality=100).url),
        'small_preview_url': str(get_thumbnail(instance.file, '100x100', crop='center', quality=100).url)
    }


