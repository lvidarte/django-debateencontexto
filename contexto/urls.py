from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from revista.views import proximamente


urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^cache/', include('contexto.cache.urls')),
    url(r'', include('contexto.revista.urls')),
    #url(r'^home/', include('contexto.revista.urls')),
    #url(r'^$', proximamente),
)

# Serve images from media in development
if settings.DEBUG:
    import os.path
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(settings.PROJECT_PATH, 'media')}),
    )
