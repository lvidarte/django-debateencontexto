# -*- coding: utf-8 -*-

from django.template.loader import render_to_string


def parse_tags(text, images):
    """
    Image:   {{img_name}}
    Resize:  {{img_name size}}
    Thumb:   {{img_name size target_name}}
    """
    import re

    tags = re.findall('\{\{[^\}]+\}\}', text)
    tags_count = len(tags)

    for tag in tags:
        align = get_align(tag)
        tokens = tag.strip('{} ').split()
        html = get_html(tokens, align, images, tags_count)
        if html:
            text = text.replace(tag, html)

    return text

def get_align(tag):
    if tag[2] == ' ' and tag[-3] == ' ':
        return 'align-center'
    elif tag[2] == ' ':
        return 'align-right'
    elif tag[-3] == ' ':
        return 'align-left'
    else:
        return ''

def get_html(tokens, align, images, tags_count):
    tokens_count = len(tokens)
    if tokens_count not in (1, 2, 3, 4):
        return

    image = get_image(tokens[0], images)
    if not image:
        return

    if tokens_count > 1:
        if not tokens[1].isdigit():
            return
        image_width = int(tokens[1])

    if tokens_count > 2:
        target = get_image(tokens[2], images)
        if not target:
            return
        rel = 'gallery' if tags_count == 1 else 'gallery[body]'

    if tokens_count > 3:
        if not tokens[3].isdigit():
            return
        target_width = int(tokens[3])

    return render_to_string('revista/minibloques/imagen_cuerpo.html', locals())

def get_html_old(tokens, align, images, tags_count):
    html = '<div%s>' % (' class="%s"' % align if align else '')
    image = get_image(tokens[0], images)
    if len(tokens) == 1:
        html += '<img src="%s" alt="%s" title="%s" />' % (image.get_absolute_url(), image.alt, image.epigrafe)
    if len(tokens) == 2:
        width = int(tokens[1])
        html += '<img src="/cache/%d%s" alt="%s" title="%s" />' % (width, image.get_absolute_url(), image.alt, image.epigrafe)
    if len(tokens) == 3:
        image2 = get_image(tokens[2], images)
        width = int(tokens[1])
        rel = 'prettyPhoto' if tags_count == 1 else 'prettyPhoto[gallery]'
        html += '<a href="%s" title="%s", rel="%s"><img src="/cache/%d%s" alt="%s" title="%s"></a>' % (image2.get_absolute_url(), image2.epigrafe, rel, width, image.get_absolute_url(), image.alt, image.epigrafe)
    html += '</div>'
    return html

def get_image(image_name, images):
    for image in images:
        if image.nombre == image_name:
            return image

