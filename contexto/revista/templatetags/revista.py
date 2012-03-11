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

