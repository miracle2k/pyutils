"""
    Graphic and Image related functionality for Pyhton.
"""

import os
import types
from PIL import Image  

"""
    Create a thumbnail of an image, and return it (as a PIL image object).
    
    Parameters:
        * new_width, new_height:
            Obviously, the wanted size of the image. Usually smaller than
            the orginal, although both directions work.
            
        * mode:
            Supports "crop", "extend" and "fit".
                crop:       Keep propertions by cropping the image.
                extend:     Keep propertions by extending the canvas.
                fit:        Do not make an effort to keep proportions.
                
        * save_to:
            If this is given, not only is the thumbnail image returned, but 
            the function will also attempt to save it at the path specified.
            Can also be a function (or lambda) that returns the path. It will
            be called with three parameters: image (the Image object), and
            new_width and new_height. For example, you can use image.format
            to determine the extension.
            
        * force:
            If this is False (default: True), the function will attempt to 
            compare the timestamps of the orginal and thumbnail images, and
            only recreate the image if the thumbnail is older than the image.
            
    # TODO: mode "extend" does not support enlarging if images
    
    Partially based on code from thsi article:
        http://batiste.dosimple.ch/blog/2007-05-13-1/
"""
def make_thumbnail(image, new_width, new_height, mode="crop", save_to=False, 
                   force=True):
    # if image is a string (=filename), open it first
    if isinstance(image, basestring):
        org_img = Image.open(image)
    elif isinstance(image, Image.Image):
        org_img = image
    else:
        raise TypeError('image must be an image object or a string')
        
    # if we are supposed to save the image as well, determine the filename 
    # right now, so we can also check whether the thumbnail *needs* 
    # regenerating at all.
    if save_to:
        if isinstance(save_to, types.FunctionType):
            new_filename = save_to(org_img, new_width, new_height)
        else:
            new_filename = save_to
    else: 
        new_filename = None    
            
    # if force is disabled, compare timestamps to determine if
    # creation is necessary.
    if (not force) and new_filename:
        if os.path.exists(new_filename) and \
            os.path.getmtime(image) <= os.path.getmtime(new_filename):
                # and we're done! ;)
                return org_img
    
    # resize the image depending on mode    
    if mode == "crop":        
        org_width, org_height = org_img.size
        crop_ratio = new_width / float(new_height)
        image_ratio = org_width / float(org_height)
        if crop_ratio < image_ratio:  
            # width needs to shrink  
            top = 0
            bottom = org_width
            crop_width = int(org_width * crop_ratio)  
            left = (org_width - crop_width) // 2  
            right = left + crop_width  
        else:  
            # height needs to shrink
            left = 0  
            right = org_width  
            crop_height = int(org_width * crop_ratio)  
            top = (org_height - crop_height) // 2  
            bottom = top + crop_height
        # actually resize the image
        new_img = org_img.crop((left, top, right, bottom)).resize(
            (new_width,new_height), Image.ANTIALIAS)
    elif mode == "fit":
        new_img = org_img.resize((new_width,new_height), Image.ANTIALIAS)
    elif mode == 'extend':
        # we can use the builtin function for parts of the job     
        thumb_img = org_img.copy()
        thumb_img.thumbnail((new_width, new_height), Image.ANTIALIAS)
        thumb_width, thumb_height = thumb_img.size
        # extend canvas whith whitespace
        print "test"
        new_img = Image.new("RGB", (new_width, new_height), "white")
        new_img.paste(thumb_img, ((new_width-thumb_width)//2, (new_height-thumb_height)//2))
    else:
        raise Exception("'%s' is not a supported mode" % mode)

    # if we're instructed to save the file, do it
    if new_filename:        
        print new_filename
        new_img.save(new_filename, org_img.format)        
        
    # return the new image in any case    
    return new_img