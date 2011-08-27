# -*- coding: utf-8 -*-

from django import template
from contexto.revista.models import Tag


register = template.Library()


# {{{ bloque_menu
@register.inclusion_tag('revista/bloques/menu.html')
def bloque_menu():
    tags = Tag.objects.filter(en_menu=True)
    tags = tags.order_by('padre', 'orden')

    menus = []
    for tag in tags:
        menu = []
        if tag.padre_id is None:
            menu.append(tag)
            for subtag in tags:
                if subtag.padre_id == tag.id:
                    menu.append(subtag)
            menus.append(menu[:])

    del menu

    return locals()
# }}}

