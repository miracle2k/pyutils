"""Thumbnail creation.

    Some of the code was originally adapted from:
        http://batiste.dosimple.ch/blog/2007-05-13-1/


All thumbnail creation functions support at least the following
arguments:

``image``:
    May be a filename, or a PIL ``Image`` instance.

``new_width``:
    The requested width of the thumbnail.

``new_height``:
    The requested height of the thumbnail.

``save_to``:
    If specified, the thumbnail will be saved to this location after
    it has been created. Enabless the ``force`` argument. You may
    also pass a callable that returns the target filename, which
    will be given three arguments: The PIL image object, the requested
    width and the requested height. You can then also use, e.g.
    ``image.format`` to determine the extension.

``force``:
    Only used if ``save_to`` is set. Defaults to ``False``. If ``True``,
    the thumbnail will always be created and saved. Otherwise, the
    timestamps of source and target are compared, and the thumbnail is
    only created if the values differ. This will only work if ``image``
    was given as a filename, otherwise ``force`` is always ``True``.

All functions return the final thumbnail as a PIL image object.
"""

from os import path
import types
from PIL import Image


__all__ = ('crop', 'fit', 'extend',)


def _common(f):
    """Handles functionality common to all thumbnail functions.

    Provides the keyword arguments ``save_to`` and ``force``.
    """
    def wrapped(image, new_width, new_height, *args, **kwargs):
        save_to = kwargs.pop('save_to', None)
        force = kwargs.pop('force', False)

        # TODO: Instead of passing the image object to the save_to()
        # call, we could simply pass the source filename. This would
        # allow us to move this code further below so that we only
        # open the image file once the timestamp comparison determined
        # that we actually have to.
        if isinstance(image, basestring):
            source_filename = image
            image = Image.open(image)
        else:
            source_filename = None
            force = True  # no filename => detection disabled

        thumb_filename = None
        if save_to:
            thumb_filename = save_to(image, new_width, new_height) \
                if callable(save_to) \
                else save_to

        if save_to and not force:
            if path.exists(thumb_filename):
                if path.getmtime(source_filename) <= path.getmtime(thumb_filename):
                    return image

        result = f(image, new_width, new_height, *args, **kwargs)

        if result and save_to:
            result.save(thumb_filename, image.format)
        return result
    return wrapped


@_common
def fit(image, new_width, new_height):
    """Resize the source image to fit the requested thumbnail size,
    without necessarily keeping proportions the same.
    """
    return image.resize((new_width, new_height), Image.ANTIALIAS)


@_common
def crop(image, new_width, new_height):
    """Resize the source image to fit the requested thumbnail size,
    but crop when necessary to keep propertions the same.
    """
    image_width, image_height = image.size
    thumb_ratio = new_width / float(new_height)
    image_ratio = image_width / float(image_height)
    if thumb_ratio < image_ratio:  # width needs to shrink
        top = 0
        bottom = image_width
        thumb_width = int(org_width * crop_ratio)
        left = (image_width - thumb_width) // 2
        right = left + thumb_width
    else:                          # height needs to shrink
        left = 0
        right = image_width_width
        thumb_height = int(image_width * thumb_ratio)
        top = (new_height - thumb_height) // 2
        bottom = top + thumb_height
    return image.crop((left, top, right, bottom)).\
        resize((new_width, new_height), Image.ANTIALIAS)


@_common
def extend(image, new_width, new_height):
    """Resize the source image while keeping propertions to fit either
    the requested width or height, and then extend the canvas to fit
    the requested thumbnail size.

    # TODO: Does currently not support enlarging of images.
    """
    thumb_img = image.copy()
    thumb_img.thumbnail((new_width, new_height), Image.ANTIALIAS)
    thumb_width, thumb_height = thumb_img.size

    # extend canvas with whitespace
    result = Image.new("RGB", (new_width, new_height), "white")
    result.paste(thumb_img, ((new_width-thumb_width)//2, (new_height-thumb_height)//2))
    return result