from django.contrib import admin

from common.mixins import ViewOnSiteMixin
from characters.models import Character, CharacterVersion, CharacterShowcase

# Data import export
from .resource import CharacterVersionResource, CharacterShowcaseResource, CharacterResource

from import_export.admin import ImportExportModelAdmin

class CharacterVersionAdmin(admin.StackedInline):
    model = CharacterVersion
    autocomplete_fields = ['static_asset', 'preview_video_static_asset']
    extra = 0
    fieldsets = (
        (
            None,
            {
                'fields': (
                    ('is_published', 'is_free', 'number', 'min_blender_version'),
                    'date_published',
                )
            },
        ),
        (
            None,
            {'fields': (('static_asset', 'preview_video_static_asset', 'preview_youtube_link'),)},
        ),
        (None, {'fields': (('description','description_en',),)}),
        (None, {'fields': (('description_zh_hans','description_zh_hant',),)}),
    )


class CharacterShowcaseAdmin(admin.StackedInline):
    model = CharacterShowcase
    autocomplete_fields = ['static_asset', 'preview_video_static_asset']
    extra = 0
    fieldsets = (
        (None, {'fields': (('is_published', 'is_free', 'min_blender_version'), 'date_published')}),
        (
            None,
            {'fields': (('static_asset', 'preview_video_static_asset', 'preview_youtube_link'),)},
        ),
        (None, {'fields': (('title', 'title_en'),)}),
        (None, {'fields': (('title_zh_hans', 'title_zh_hant'),)}),
        (None, {'fields': (('description', 'description_en'),)}),
        (None, {'fields': (('description_zh_hans', 'description_zh_hant'),)}),
    )


@admin.register(Character)
class CharacterAdmin(ImportExportModelAdmin, ViewOnSiteMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = [
        '__str__',
        'film',
        'is_published',
        'date_published',
        'view_link',
    ]
    list_filter = [
        'is_published',
        'film',
    ]
    autocomplete_fields = ['film']
    prepopulated_fields = {
        'slug': ('name',),
    }
    inlines = [CharacterVersionAdmin, CharacterShowcaseAdmin]

    resource_class = CharacterResource

@admin.register(CharacterVersion)
class CharacterVersionResourceAdmin(ImportExportModelAdmin, ViewOnSiteMixin, admin.ModelAdmin):
    list_display = [
        'character',
        'min_blender_version',
        'is_published',
        'date_published',
        'view_link',
    ]

    resource_class = CharacterVersionResource


@admin.register(CharacterShowcase)
class CharacterShowcaseResourceAdmin(ImportExportModelAdmin, ViewOnSiteMixin, admin.ModelAdmin):
    list_display = [
        'character',
        'min_blender_version',
        'is_published',
        'date_published',
        'view_link',
    ]

    resource_class = CharacterShowcaseResource