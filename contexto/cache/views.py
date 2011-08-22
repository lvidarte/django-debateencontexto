# -*- coding: utf-8 -* -

import os.path
import Image, ImageDraw
import math

from django.conf import settings
from django.http import HttpResponse


def img(request, url, width): # {{{
    img_path = os.path.join(settings.MEDIA_ROOT, url[1:])
    try:
        image = Image.open(img_path)
        w, h = image.size
    except:
        raise Http404()
    else:
        width = int(width)
        height = int(math.ceil(float(width) * float(h) / float(w)))

        if width and height:
            image.thumbnail((width, height), Image.ANTIALIAS)
            draw = ImageDraw.Draw(image)
            #draw.text((5,5), "%dx%d" % (width, height))
            #draw.text((5,5), datetime.now().strftime('%H:%M:%S'))
            response = HttpResponse(mimetype="image/%s"%image.format)
            image.save(response, image.format, quality=90)
            return response
        else:
            raise Http404()
# }}}

