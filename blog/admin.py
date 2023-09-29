from django.contrib import admin
from django.forms import Textarea

from blog.models import Post
from common.mixins import ViewOnSiteMixin
import search.signals

# Data import export
from .resource import PostResource

from import_export.admin import ImportExportModelAdmin

@admin.register(Post)
class PostAdmin(ImportExportModelAdmin, ViewOnSiteMixin, admin.ModelAdmin):
    list_display = [
        '__str__',
        'film',
        'author',
        'is_published',
        'date_published',
        'view_link',
    ]
    list_filter = [
        'is_published',
        'film',
    ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Override display of "excerpt" field.

        Make it appear smaller than the content text area.
        """
        if db_field.name == 'excerpt':
            kwargs['widget'] = Textarea(attrs={'rows': 2, 'cols': 40})
        return super().formfield_for_dbfield(db_field, **kwargs)

    fields = (
        'date_published',
        'title_en',
        'title_zh_hans',
        'title_zh_hant',
        'slug',
        'category',
        'author',
        'film',
        'excerpt_en',
        'excerpt_zh_hans',
        'excerpt_zh_hant',
        'content_en',
        'content_zh_hans',
        'content_zh_hant',
        'attachments',
        'header',
        'thumbnail',
        'is_published',
    )
    autocomplete_fields = ['author', 'attachments', 'film']
    search_fields = ['slug']
    prepopulated_fields = {
        'slug': ('title_en',),
    }

    # actions = [search.signals.reindex]
    
    resource_class = PostResource