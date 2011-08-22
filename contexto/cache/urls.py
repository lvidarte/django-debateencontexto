# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns

urlpatterns = patterns('contexto.cache.views',
    (r'^(?P<width>\d{2,3})(?P<url>.+)$', 'img', {}, 'contexto-cache-img'),
)

