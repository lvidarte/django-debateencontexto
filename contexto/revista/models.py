# -*- coding: utf-8 -*-

import markdown

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User as Editor

from PIL import Image
from mimetypes import guess_type
from datetime import datetime

from contexto.revista.managers import PublicManager
from contexto.revista.parser import parse_tags


SINO_CHOICES = (
    (True, 'Sí'),
    (False, 'No'),
)

TIPOS_CHOICES = (
    ('fotografo', 'Fotógrafo'),
    ('periodista', 'Periodista'),
    ('agencia', 'Agencia'),
    ('corresponsal', 'Corresponsal'),
    ('columnista', 'Columnista'),
    ('otro', 'Otro'),
)

JERARQUIA_CHOICES = (
    ('normal', 'Normal'),
    ('destacada', 'Destacada'),
    ('secundaria', 'Secundaria'),
)

HELP_TEXT_IMAGES = '''{{image size full_image full_image_size}}<br>
                      {{#audio nombre|url}}
                   '''


class Archivo(models.Model):
    file = models.FileField(upload_to='%Y/%m/%d', max_length=512,
        verbose_name='archivo')
    alt = models.CharField(max_length=255, blank=True,
        verbose_name='alt',
        help_text='Descripción de la imagen')
    descripcion = models.TextField(blank=True,
        verbose_name='descripción')
    size = models.IntegerField(blank=True, default=0,
        verbose_name='tamaño')
    mime = models.CharField(max_length=255, blank=True)
    width = models.IntegerField(blank=True, default=0,
        verbose_name='ancho')
    height = models.IntegerField(blank=True, default=0,
        verbose_name='alto')
    is_image = models.BooleanField(blank=True, default=False,
        verbose_name='imagen')
    autor = models.ForeignKey('Autor', blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True, null=True)

    # Datos creación
    editor_creacion = models.ForeignKey(Editor, blank=True,
        related_name='archivo_creado_por', verbose_name='creado por')
    fecha_creacion = models.DateTimeField(auto_now_add=True,
        verbose_name='creado el')

    # Datos última modificación
    editor_modificacion = models.ForeignKey(Editor, blank=True,
        related_name='archivo_modificado_por', verbose_name='modificado por')
    fecha_modificacion = models.DateTimeField(auto_now=True,
        verbose_name='modificado el')

    class Meta:
        verbose_name_plural = 'archivos'

    def es_imagen(self):
        return self.is_image

    def get_fecha_modificacion(self):
        if self.fecha_modificacion == self.fecha_creacion:
            return ''
        else:
            return self.fecha_modificacion.strftime(settings.TXT_DATETIME_FORMAT)

    get_fecha_modificacion.short_description = 'fecha modificación'

    def get_editor_modificacion(self):
        if self.fecha_modificacion == self.fecha_creacion:
            return ''
        else:
            return self.editor_modificacion

    get_editor_modificacion.short_description = 'modificado por'

    def get_fecha_creacion(self):
        return self.fecha_creacion.strftime(settings.TXT_DATETIME_FORMAT)

    get_fecha_creacion.short_description = 'fecha creación'
    get_fecha_creacion.admin_order_field = 'fecha_creacion'

    def get_size(self):
        if self.size < 1024: # < 1Kib
            return "%s bytes" % self.size
        elif self.size < 1048576: # < 1Mib
            return "%s Kib" % round(self.size / float(1024), 1)
        else: # >= 1Mib
            return "%s Mib" % round(self.size / float(1048576), 1)

    get_size.short_description = 'tamaño'
    get_size.allow_tags = True
    get_size.admin_order_field = 'size'

    def thumbnail(self):
        if self.is_image:
            return u'<img src="%s" width="100px" />' % self.get_absolute_url()

    thumbnail.short_description = 'miniatura'
    thumbnail.allow_tags = True

    def get_absolute_url(self):
        return self.file.url

    def save(self, force_insert=False, force_update=False):
        setattr(self, 'size', self.file.size) 
        mime = guess_type(self.file.name)[0]
        setattr(self, 'mime', mime) 

        if mime.split('/')[0] == 'image':
            setattr(self, 'is_image', 1) 
            img = Image.open(self.file)
            width, height = img.size
            setattr(self, 'width', width) 
            setattr(self, 'height', height) 

        super(Archivo, self).save(force_insert, force_update)

    def __unicode__(self):
        if self.alt:
            return self.alt
        else:
            return self.file.name

class Autor(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True,
        help_text='URL del listado de notas del autor')
    email = models.EmailField(max_length=128, blank=True)
    web = models.URLField(max_length=255, blank=True,
        help_text='Blog/página web personal')
    comentario = models.TextField(max_length=512, blank=True)
    foto = models.OneToOneField('Archivo', blank=True, null=True, related_name='+')
    tipo = models.CharField(max_length=64, default='periodista',
        choices=TIPOS_CHOICES)
    estado = models.BooleanField(default=True,
        choices=SINO_CHOICES, verbose_name='activo')

    class Meta:
        verbose_name_plural = 'autores'

    def get_estado(self):
        return self.estado

    get_estado.short_description = 'activo'
    get_estado.boolean = True
    get_estado.admin_order_field = 'estado'

    @models.permalink
    def get_absolute_url(self):
        return ('contexto-revista-notas-autor', (), {'slug': self.slug})

    def __unicode__(self):
        return " ".join([x for x in (self.nombre, self.apellido) if x])

class Nota(models.Model):
    fecha = models.DateField(default=datetime.now())
    hora = models.TimeField(default=datetime.now())
    autores = models.ManyToManyField('Autor', blank=True, null=True,
        through='NotaAutores')
    titulo = models.CharField(max_length=255, blank=True,
        verbose_name='título')
    slug = models.SlugField(max_length=255, unique_for_date='fecha',
        help_text='URL de la nota (debería ser el título de la nota)')
    copete_markdown = models.TextField(blank=True, verbose_name='copete')
    copete = models.TextField(blank=True)
    cuerpo_markdown = models.TextField(blank=True, verbose_name='cuerpo',
        help_text=HELP_TEXT_IMAGES)
    cuerpo_html = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    archivos = models.ManyToManyField('Archivo', blank=True, null=True,
        through='NotaArchivos')
    es_galeria = models.BooleanField(default=False, choices=SINO_CHOICES,
        verbose_name='es galería')
    orden = models.IntegerField(default=0)
    estado = models.BooleanField(default=False,
        choices=SINO_CHOICES, verbose_name='visible')
    jerarquia = models.CharField(max_length=64, default='normal',
        choices=JERARQUIA_CHOICES, verbose_name='jerarquía')
    es_titular = models.BooleanField(default=True,
        choices=SINO_CHOICES, verbose_name='es titular')
    relacionadas = models.ManyToManyField('Nota', blank=True, null=True,
        verbose_name='notas relacionadas')
    permitir_comentarios = models.BooleanField(default=True,
        choices=SINO_CHOICES)

    # Datos creación
    editor_creacion = models.ForeignKey(Editor, blank=True,
        related_name='nota_creado_por', verbose_name='creado por')
    fecha_creacion = models.DateTimeField(auto_now_add=True,
        verbose_name='creado el')

    # Datos última modificación
    editor_modificacion = models.ForeignKey(Editor, blank=True,
        related_name='nota_modificado_por', verbose_name='modificado por')
    fecha_modificacion = models.DateTimeField(auto_now=True,
        verbose_name='modificado el')

    @property
    def cuerpo(self):
        return parse_tags(self.cuerpo_html, self.get_archivos())

    # Manager
    objects = PublicManager()

    def get_estado(self):
        return self.estado

    get_estado.short_description = 'visible'
    get_estado.boolean = True
    get_estado.admin_order_field = 'estado'

    @models.permalink
    def get_absolute_url(self):
        #import pdb; pdb.set_trace()
        return ('contexto-revista-nota', (), {
                    'year': self.fecha.strftime('%Y'),
                    'month': self.fecha.strftime('%m'),
                    'day': self.fecha.strftime('%d'),
                    'slug': self.slug})

    def get_autores(self):
        if not getattr(self, '_autores', False):
            self._autores = []
            for na in self.notaautores_set.order_by('orden'):
                autor = na.autor
                autor.orden = na.orden
                self._autores.append(autor)
        return self._autores

    def get_archivos(self):
        if not getattr(self, '_archivos', False):
            self._archivos = []
            for na in self.notaarchivos_set.order_by('orden'):
                archivo = na.archivo
                archivo.epigrafe = na.epigrafe
                archivo.orden = na.orden
                archivo.nombre = na.nombre
                archivo.en_galeria = na.en_galeria
                archivo.en_titular = na.en_titular
                self._archivos.append(archivo)
        return self._archivos

    def get_imagenes(self):
        imagenes = []
        for archivo in self.get_archivos():
            if archivo.es_imagen():
                imagenes.append(archivo)
        return imagenes

    def imagenes_count(self):
        return len(self.get_imagenes())

    def imagenes_en_galeria_count(self):
        total = 0
        for imagen in self.get_imagenes():
            if imagen.en_galeria:
                total += 1
        return total

    def get_imagen_titular(self):
        for imagen in self.get_imagenes():
            if imagen.en_titular:
                return imagen

    def get_anterior(self):
        notas = Nota.objects.filter(
                        publicacion=self.publicacion,
                        seccion=self.seccion,
                        fecha__lt=self.fecha).order_by('-fecha')[:1]
        if len(notas):
            return notas[0]

    def get_siguiente(self):
        notas = Nota.objects.filter(
                        publicacion=self.publicacion,
                        seccion=self.seccion,
                        fecha__gt=self.fecha).order_by('fecha')[:1]
        if len(notas):
            return notas[0]

    def save(self, force_insert=False, force_update=False):
        self.copete = markdown.markdown(self.copete_markdown)
        self.cuerpo_html = markdown.markdown(self.cuerpo_markdown)
        if self.slug == '':
            self.slug = 'sin-titulo'
        super(Nota, self).save(force_insert, force_update)

    def __unicode__(self):
        return '%s [%s] %s' % (self.id,
            self.fecha.strftime('%Y-%m-%d'), self.titulo)

class NotaArchivos(models.Model):
    nota = models.ForeignKey('Nota')
    archivo = models.ForeignKey('Archivo')
    nombre = models.CharField(max_length=64, blank=True)
    epigrafe = models.TextField(blank=True,
        verbose_name='epígrafe')
    en_galeria = models.BooleanField(default=True, choices=SINO_CHOICES,
        verbose_name='en galería')
    en_titular = models.BooleanField(default=False, choices=SINO_CHOICES)
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = 'revista_nota_archivos'
        verbose_name = 'archivo de la nota'
        verbose_name_plural = 'archivos de la nota'

    def thumbnail(self, width=100):
        return self.archivo.thumbnail(width)

    thumbnail.short_description = 'miniatura'
    thumbnail.allow_tags = True

    def __unicode__(self):
        return self.archivo.__unicode__()

    def get_autores(self):
        return self.archivo.ArchivoAutores_set.all()

class NotaAutores(models.Model):
    nota = models.ForeignKey('Nota')
    autor = models.ForeignKey('Autor')
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = 'revista_nota_autores'
        verbose_name = 'autor de la nota'
        verbose_name_plural = 'autores de la nota'

    def __unicode__(self):
        return ", ".join((self.autor.apellido, self.autor.nombre))

class Pagina(models.Model):
    titulo = models.CharField(max_length=255, blank=True,
        verbose_name='título')
    url = models.CharField(max_length=255, unique=True,
        help_text='URL de la página (debería ser el título de la página)')
    copete_markdown = models.TextField(blank=True, verbose_name='copete')
    copete = models.TextField(blank=True)
    cuerpo_markdown = models.TextField(blank=True, verbose_name='cuerpo',
        help_text=HELP_TEXT_IMAGES)
    cuerpo_html = models.TextField(blank=True)
    archivos = models.ManyToManyField('Archivo', blank=True, null=True,
        through='PaginaArchivos')
    estado = models.BooleanField(default=False,
        choices=SINO_CHOICES, verbose_name='visible')
    permitir_comentarios = models.BooleanField(default=True,
        choices=SINO_CHOICES)

    # Datos creación
    editor_creacion = models.ForeignKey(Editor, blank=True,
        related_name='pagina_creado_por', verbose_name='creado por')
    fecha_creacion = models.DateTimeField(auto_now_add=True,
        verbose_name='creado el')

    # Datos última modificación
    editor_modificacion = models.ForeignKey(Editor, blank=True,
        related_name='pagina_modificado_por', verbose_name='modificado por')
    fecha_modificacion = models.DateTimeField(auto_now=True,
        verbose_name='modificado el')

    @property
    def cuerpo(self):
        return parse_tags(self.cuerpo_html, self.get_archivos())

    # Manager
    objects = PublicManager()

    def get_estado(self):
        return self.estado

    get_estado.short_description = 'visible'
    get_estado.boolean = True
    get_estado.admin_order_field = 'estado'

    @models.permalink
    def get_absolute_url(self):
        return ('contexto-revista-pagina', (), {'url': self.url})

    def get_archivos(self):
        if not getattr(self, '_archivos', False):
            self._archivos = []
            for pa in self.paginaarchivos_set.order_by('orden'):
                archivo = pa.archivo
                archivo.epigrafe = pa.epigrafe
                archivo.orden = pa.orden
                archivo.nombre = pa.nombre
                archivo.en_galeria = pa.en_galeria
                archivo.en_titular = pa.en_titular
                self._archivos.append(archivo)
        return self._archivos

    def get_imagenes(self):
        imagenes = []
        for archivo in self.get_archivos():
            if archivo.es_imagen:
                imagenes.append(archivo)
        return imagenes

    def imagenes_count(self):
        return len(self.get_imagenes())

    def imagenes_en_galeria_count(self):
        total = 0
        for imagen in self.get_imagenes():
            if imagen.en_galeria:
                total += 1
        return total

    def get_imagen_titular(self):
        for imagen in self.get_imagenes():
            if imagen.en_titular:
                return imagen

    def save(self, force_insert=False, force_update=False):
        self.copete = markdown.markdown(self.copete_markdown)
        self.cuerpo_html = markdown.markdown(self.cuerpo_markdown)
        if self.url == '':
            self.url = 'sin-titulo'
        super(Pagina, self).save(force_insert, force_update)

    def __unicode__(self):
        return '%s %s' % (self.id, self.titulo)

class PaginaArchivos(models.Model):
    nota = models.ForeignKey('Pagina')
    archivo = models.ForeignKey('Archivo')
    nombre = models.CharField(max_length=64, blank=True)
    epigrafe = models.TextField(blank=True,
        verbose_name='epígrafe')
    en_galeria = models.BooleanField(default=True, choices=SINO_CHOICES,
        verbose_name='en galería')
    en_titular = models.BooleanField(default=False, choices=SINO_CHOICES)
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = 'revista_pagina_archivos'
        verbose_name = 'archivo de la página'
        verbose_name_plural = 'archivos de la página'

    def thumbnail(self, width=100):
        return self.archivo.thumbnail(width)

    thumbnail.short_description = 'miniatura'
    thumbnail.allow_tags = True

    def __unicode__(self):
        return self.archivo.__unicode__()

    def get_autores(self):
        return self.archivo.ArchivoAutores_set.all()

class Tag(models.Model):
    nombre = models.CharField(max_length=128)
    slug = models.SlugField(max_length=255, unique=True,
        help_text='URL del listado de notas relacionadas con el tag')
    url = models.CharField(max_length=255, blank=True, null=True,
        help_text='URL de la página estática')
    en_menu = models.BooleanField(default=False,
        choices=SINO_CHOICES, verbose_name='En menú?',
        help_text='¿Se muestra en el menú?')
    padre = models.ForeignKey('Tag', blank=True, null=True,
        help_text='¿De quién es submenú?')
    orden = models.IntegerField(default=0,
        help_text='Orden dentro del nivel en que se encuentra')

    def get_en_menu(self):
        return self.en_menu

    get_en_menu.short_description = 'En menú'
    get_en_menu.boolean = True
    get_en_menu.admin_order_field = 'en_menu'

    @models.permalink
    def get_absolute_url(self):
        return ('contexto-revista-notas-tag', (), {'slug': self.slug})

    def __unicode__(self):
        return self.nombre

