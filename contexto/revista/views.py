# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404

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
    return HttpResponse('nota del %s/%s/%s y slug %s ' % (year, month, day, slug))
# }}}

