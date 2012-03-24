# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.views.generic import list_detail

from contexto.revista.models import Nota, Pagina, Tag, Autor


PAGINATE_BY = 4


def portada(request, page=1):
    if page is None:
        page = 1

    if page == 1:
        template_name = 'revista/portada.html'
    else:
        template_name = 'revista/portada_anteriores.html'

    queryset = Nota.objects.published()
    queryset = queryset.order_by('-fecha', 'orden', '-hora')

    return list_detail.object_list(
        request,
        queryset=queryset,
        page=page,
        paginate_by=PAGINATE_BY,
        template_name=template_name,
        extra_context={})

def listado_tags(request):
    query = """ SELECT t.id, t.nombre, t.slug
                FROM revista_tag AS t
                INNER JOIN revista_nota_tags AS nt
                    ON t.id=nt.tag_id
                INNER JOIN revista_nota AS n
                    ON nt.nota_id=n.id AND n.estado=1 """

    tags = Tag.objects.raw(query)
    return render_to_response('revista/listado_tags.html', {'tags': tags},
        context_instance=RequestContext(request))

def listado_notas_tag(request, slug, page=1):
    if page is None:
        page = 1

    tag = Tag.objects.get(slug=slug)

    queryset = Nota.objects.published()
    queryset = queryset.filter(tags__id=tag.id)
    queryset = queryset.order_by('-fecha', 'orden', '-hora')

    return list_detail.object_list(
        request,
        queryset=queryset,
        paginate_by=PAGINATE_BY,
        page=page,
        template_name='revista/listado_notas_tag.html',
        extra_context={'tag': tag})

def listado_autores(request):
    return HttpResponse('listado de autores')

def listado_notas_autor(request, slug, page=1):
    if page is None:
        page = 1

    autor = Autor.objects.get(slug=slug)

    queryset = Nota.objects.published()
    queryset = queryset.filter(autores__id=autor.id)
    queryset = queryset.order_by('-fecha', 'orden', '-hora')

    return list_detail.object_list(
        request,
        queryset=queryset,
        paginate_by=PAGINATE_BY,
        page=page,
        template_name='revista/listado_notas_autor.html',
        extra_context={'autor': autor})

def nota(request, year, month, day, slug):
    return render_to_response('revista/nota.html', 
        {'nota': Nota.objects.get(fecha__year=int(year),
                                  fecha__month=int(month),
                                  fecha__day=int(day),
                                  slug=slug)},
        context_instance=RequestContext(request))

def pagina(request, url):
    return render_to_response('revista/pagina.html', 
        {'pagina': Pagina.objects.get(url=url)},
        context_instance=RequestContext(request))

