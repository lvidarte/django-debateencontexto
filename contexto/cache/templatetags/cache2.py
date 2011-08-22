# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse


register = template.Library()

@register.filter
def thumb(url, width):
    if url:
        return reverse('contexto-cache-img', kwargs={'width':width, 'url':url})

