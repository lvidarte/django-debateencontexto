# -*- coding: utf-8 -*-

def parse_tags(text, images):
    """
    Image:   {{img_name}}
    Resize:  {{img_name size}}
    Thumb:   {{img_name size target_name}}
    """
    import re

    for tag in re.findall('\{\{[^\}]+\}\}', text):
        align = get_align(tag)
        tokens = tag.strip('{} ').split()
        text = text.replace(tag, get_html(tokens, align, images))

    return text

def get_align(tag):
    if tag[2] == ' ' and tag[-3] == ' ':
        return 'align-center'
    elif tag[2] == ' ':
        return 'align-right'
    elif tag[-3] == ' ':
        return 'align-left'

def get_html(tokens, align, images):
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
        html += '<a href="%s" title="%s", rel="prettyPhoto[gallery]"><img src="/cache/%d%s" alt="%s" title="%s"></a>' % (image2.get_absolute_url(), image2.epigrafe, width, image.get_absolute_url(), image.alt, image.epigrafe)
    html += '</div>'
    return html

def get_image(image_name, images):
    for image in images:
        if image.nombre == image_name:
            return image
