# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User as Editor

from PIL import Image
from mimetypes import guess_type
from datetime import datetime

from contexto.revista.managers import PublicManager


SINO_CHOICES = (
    (True, 'Si'),
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


class Archivo(models.Model): # {{{
    file = models.FileField(upload_to='archivos/%Y/%m/%d', max_length=512,
        verbose_name='archivo')
    alt = models.CharField(max_length=256, blank=True,
        verbose_name='alt', help_text='Descripción de la imagen (no videntes)')
    descripcion = models.TextField(blank=True,
        verbose_name='descripción')
    size = models.IntegerField(blank=True, default=0,
        verbose_name='tamaño')
    mime = models.CharField(max_length=256, blank=True)
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
            return u'<img src="/static%s" width="100px" />' % self.file.url

    thumbnail.short_description = 'miniatura'
    thumbnail.allow_tags = True

    def get_absolute_url(self):
        return '/static' + self.file.url

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
        return self.file.name
# }}}
class Autor(models.Model): # {{{
    nombre = models.CharField(max_length=256)
    apellido = models.CharField(max_length=256, blank=True)
    slug = models.SlugField(max_length=256, unique=True,
        help_text='URL del listado de notas del autor')
    email = models.EmailField(max_length=128, blank=True)
    web = models.URLField(max_length=256, blank=True,
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
# }}}
class Nota(models.Model): # {{{
    fecha = models.DateField(default=datetime.now())
    hora = models.TimeField(default=datetime.now())
    autores = models.ManyToManyField('Autor', blank=True, null=True,
        through='NotaAutores')
    titulo = models.CharField(max_length=256, blank=True,
        verbose_name='Título')
    slug = models.SlugField(max_length=256, unique_for_date='fecha',
        help_text='URL de la nota (debería ser el título de la nota)')
    copete = models.TextField(blank=True)
    cuerpo = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    archivos = models.ManyToManyField('Archivo', blank=True, null=True,
        through='NotaArchivos')
    es_galeria = models.BooleanField(default=False, choices=SINO_CHOICES,
        verbose_name='Es galería')
    orden = models.IntegerField(default=0)
    estado = models.BooleanField(default=False,
        choices=SINO_CHOICES, verbose_name='visible')
    jerarquia = models.CharField(max_length=64, default='normal',
        choices=JERARQUIA_CHOICES, verbose_name='jerarquía')
    relacionadas = models.ManyToManyField('Nota', blank=True, null=True,
        verbose_name='notas relacionadas')

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

    def get_archivos(self):
        if not getattr(self, '_archivos', False):
            self._archivos = []
            for na in self.notaarchivos_set.order_by('orden'):
                archivo = na.archivo
                archivo.epigrafe = na.epigrafe
                archivo.orden = na.orden
                self._archivos.append(archivo)
        return self._archivos

    @property
    def fotos_count(self):
        return len(self.get_fotos())

    def get_fotos(self):
        fotos = []
        for archivo in self.get_archivos():
            if archivo.es_imagen:
                fotos.append(archivo)
        return fotos


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
        if self.slug == '':
            self.slug = 'sin-titulo'
        super(Nota, self).save(force_insert, force_update)

    def __unicode__(self):
        return '%s [%s] %s' % (self.id,
            self.fecha.strftime('%Y-%m-%d'), self.titulo)
# }}}
class NotaArchivos(models.Model): # {{{
    nota = models.ForeignKey('Nota')
    archivo = models.ForeignKey('Archivo')
    epigrafe = models.TextField(blank=True,
        verbose_name='epígrafe')
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

# }}}
class NotaAutores(models.Model): # {{{
    nota = models.ForeignKey('Nota')
    autor = models.ForeignKey('Autor')
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = 'revista_nota_autores'
        verbose_name = 'autor de la nota'
        verbose_name_plural = 'autores de la nota'

    def __unicode__(self):
        return ", ".join((self.autor.apellido, self.autor.nombre))
# }}}
class Tag(models.Model): # {{{
    nombre = models.CharField(max_length=128,
        verbose_name='nombre')
    slug = models.SlugField(max_length=256, unique=True,
        help_text='URL del listado de notas relacionadas con el tag')
    en_menu = models.BooleanField(default=False,
        choices=SINO_CHOICES, verbose_name='En menú?',
        help_text='¿Se muestra en el menú?')
    padre = models.OneToOneField('Tag', blank=True, null=True,
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
# }}}

