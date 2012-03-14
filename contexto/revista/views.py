# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.views.generic import list_detail

from contexto.revista.models import Nota, Pagina, Tag

def portada(request, page=0):
    notas = Nota.objects.published()
    notas = notas.order_by('-fecha', 'orden', '-hora')

    destacadas = []
    if page < 2:
        destacadas = [n for n in notas[0:20]
                      if n.jerarquia=='destacada']

    return list_detail.object_list(
        request,
        queryset=notas.exclude(jerarquia='destacada'),
        page=page,
        paginate_by=4,
        template_name='revista/portada.html',
        extra_context={'destacadas': destacadas},
    )

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

def listado_notas_tag(request, slug, page=0, paginate_by=20, **kwargs):
    notas = Nota.objects.published().filter(tags__slug=slug).order_by('-fecha')
    if not notas:
        raise Http404
    else:
        return list_detail.object_list(
            request,
            queryset=notas,
            paginate_by=paginate_by,
            page=page,
            template_name='revista/listado_notas_tag.html',
            **kwargs
        )

def listado_autores(request):
    return HttpResponse('listado de autores')

def listado_notas_autor(request, slug):
    return HttpResponse('listado de notas por autor ' + slug)

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

