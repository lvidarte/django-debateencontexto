# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.forms import TextInput, Textarea, ModelForm, Media

from contexto.revista.models import *

RESULTS_PER_PAGE = 50
TEXTAREA_SIZE = 60

# {{{ ArchivoAdmin
class ArchivoAdmin(admin.ModelAdmin):
    list_per_page = RESULTS_PER_PAGE
    filter_horizontal = ('tags',)
    list_display = (
        'file', 'thumbnail', 'get_size', 'width', 'height',
        'editor_creacion', 'get_fecha_creacion',
        'get_editor_modificacion', 'get_fecha_modificacion',
    )
    list_filter = ('fecha_creacion', 'editor_creacion', 'is_image')
    fieldsets = (
        (None, {
            'fields': ('file', 'alt'),
        }),
        ('Descripción', {
            'classes': ('collapse',),
            'fields': ('descripcion',),
        }),
        ('Tags', {
            'classes': ('collapse',),
            'fields': ('tags',),
        }),
    )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':TEXTAREA_SIZE})},
    }

    def save_model(self, request, obj, form, change):
        if not change:
            obj.editor_creacion = request.user
        obj.editor_modificacion = request.user
        obj.save()
# }}}
# {{{ AutorAdmin
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'slug', 'email', 'web', 'get_estado')
    prepopulated_fields = {'slug': ('nombre', 'apellido')}
    fieldsets = (
        (None, {
            'fields': ('nombre', 'apellido', 'slug', 'email', 'web'),
        }),
        (None, {
            'fields': ('foto',),
        }),
        (None, {
            'fields': ('tipo', 'estado',),
        }),
        ('Extra', {
            'classes': ('collapse', ),
            'fields': ('comentario',),
        }),
    )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':TEXTAREA_SIZE})},
    }

    def save_model(self, request, obj, form, change):
        obj.save()
# }}}
# {{{ NotaAdmin
class NotaAutoresInline(admin.TabularInline):
    model = NotaAutores
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'autor':
            kwargs['queryset'] = Autor.objects.order_by('apellido', 'nombre')
        return db_field.formfield(**kwargs)

class NotaArchivosInline(admin.TabularInline):
    model = NotaArchivos
    extra = 0

class NotaAdmin(admin.ModelAdmin):
    inlines = (NotaAutoresInline, NotaArchivosInline)
    date_hierarchy = 'fecha'
    list_display = (
        'titulo', 'fecha', 'hora',
        'es_galeria', 'orden', 'get_estado'
    )
    list_filter = ('fecha', 'editor_creacion')
    search_fields = ['@titulo',]
    filter_horizontal = ('tags', 'relacionadas')
    prepopulated_fields = {'slug': ('titulo',)}
    fieldsets = (
        ('Fecha y Hora', {
            'classes': ('collapse', ),
            'fields': ('fecha', 'hora'),
        }),
        (None, {
            'fields': ('titulo', 'slug', 'copete', 'cuerpo'),
        }),
        (None, {
            'fields': ('estado', 'jerarquia', 'es_galeria', 'orden'),
        }),
        ('Tags', {
            'classes': ('collapse', ),
            'fields': ('tags',),
        }),
        ('Notas relacionadas', {
            'classes': ('collapse', ),
            'fields': ('relacionadas',),
        }),
    )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':TEXTAREA_SIZE})},
        models.TextField: {'widget': Textarea(attrs={'rows':'20', 'cols':'80'})}
    }

    def save_model(self, request, obj, form, change):
        #import ipdb; ipdb.set_trace()
        if not change:
            obj.editor_creacion = request.user
        obj.editor_modificacion = request.user

        obj.save()
# }}}
# {{{ TagAdmin
class TagAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'get_en_menu', 'padre', 'orden')
    list_filter = ('en_menu',)
    prepopulated_fields = {'slug': ('nombre',)}
# }}}

admin.site.register(Archivo, ArchivoAdmin)
admin.site.register(Autor, AutorAdmin)
admin.site.register(Nota, NotaAdmin)
admin.site.register(Tag, TagAdmin)

