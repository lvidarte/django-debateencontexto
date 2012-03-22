# -*- coding: utf-8 -*-

from django import template
from contexto.revista.models import Tag


register = template.Library()


@register.inclusion_tag('revista/bloques/menu.html')
def bloque_menu():
    tags = Tag.objects.filter(en_menu=True)
    tags = tags.order_by('padre', 'orden')

    menu = []
    for tag in tags:
        subitems = []
        if tag.padre_id is None:
            item = tag
            for subtag in tags:
                if subtag.padre_id == tag.id:
                    subitems.append(subtag)
            menu.append({'item': item, 'subitems': subitems})

    return locals()

@register.inclusion_tag('revista/bloques/galeria.html')
def bloque_galeria(nota):
    return locals()

@register.inclusion_tag('revista/minibloques/volanta.html')
def bloque_volanta(nota):
    fecha = nota.fecha
    tags = nota.tags.all()
    return locals()

@register.inclusion_tag('revista/minibloques/autores.html')
def bloque_autores(nota):
    autores = nota.get_autores()
    return locals()

@register.inclusion_tag('revista/minibloques/copete.html')
def bloque_copete(nota):
    copete = nota.copete
    return locals()

@register.filter
def jerarquia(object_list, jerarquia):
    return [nota for nota in object_list
                if nota.jerarquia==jerarquia]

