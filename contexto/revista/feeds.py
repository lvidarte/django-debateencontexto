# vim: set fileencoding=utf-8 :

from django.contrib.syndication.views import Feed
from django.contrib.sites.models import Site
from contexto.revista.models import Nota
from datetime import datetime


class NotaFeeds(Feed):
    _site = Site.objects.get_current()
    title = "Contexto. Política y Sociedad."
    link = "http://%s" % _site.domain
    description = "Description Contexto"

    def items(self):
        notas = Nota.objects.published()
        notas = notas.order_by('-fecha', 'orden', '-hora')
        return notas[:15]

    def item_pubdate(self, item):
        return datetime(item.fecha.year,
                        item.fecha.month,
                        item.fecha.day,
                        item.hora.hour,
                        item.hora.minute,
                        item.hora.second)

    def item_title(self, item):
        return item.titulo

    def item_description(self, item):
        return item.copete

    def item_author_name(self, item):
        autores = ""
        sep = ""
        for autor in item.get_autores():
            autores += "%s%s %s" % (sep, autor.nombre, autor.apellido)
            sep = ", "
        return autores
