# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404

from contexto.revista.models import Nota

def index(request): # {{{
    return HttpResponse('index')
# }}}
def listado_tags(request): # {{{
    return HttpResponse('listado de tags')
# }}}
def listado_notas_tag(request, slug): # {{{
    return HttpResponse('listado de notas por tag ' + slug)
# }}}
def listado_autores(request): # {{{
    return HttpResponse('listado de autores')
# }}}
def listado_notas_autor(request, slug): # {{{
    return HttpResponse('listado de notas por autor ' + slug)
# }}}
def nota(request, year, month, day, slug): # {{{
    return render_to_response('revista/nota.html', {
        'nota': Nota.objects.get(fecha__year=int(year),
                                 fecha__month=int(month),
                                 fecha__day=int(day),
                                 slug=slug)
    })
# }}}

