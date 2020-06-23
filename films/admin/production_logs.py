import datetime as dt
from typing import Optional, Any

from django.contrib import admin
from django.db.models import ForeignKey, Q
from django.forms.models import ModelChoiceField
from django.http.request import HttpRequest
from django.utils import timezone

from films.admin.mixins import EditLinkMixin
from films.models import production_logs, Asset, ProductionLog


class ProductionLogEntryAssetInline(admin.StackedInline):
    model = production_logs.ProductionLogEntryAsset
    show_change_link = True
    extra = 0

    def formfield_for_foreignkey(
        self, db_field: 'ForeignKey[Any, Any]', request: Optional[HttpRequest], **kwargs: Any
    ) -> Optional[ModelChoiceField]:
        if db_field.name == 'asset':
            # Only show published assets created in the last 7 days by the current user
            # TODO(Natalia): add filtering by film, show assets since the last log
            kwargs['queryset'] = Asset.objects.filter(
                Q(static_asset__author=request.user)
                | (Q(static_asset__author__isnull=True) & Q(static_asset__user=request.user)),
                is_published=True,
                date_created__gte=timezone.now() - dt.timedelta(days=7),
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(production_logs.ProductionLogEntry)
class ProductionLogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'production_log__start_date'
    list_display = ['__str__', 'production_log']
    inlines = [ProductionLogEntryAssetInline]
    list_filter = ['production_log__film', 'production_log', 'user', 'author']


class ProductionLogEntryInline(EditLinkMixin, admin.StackedInline):
    model = production_logs.ProductionLogEntry
    show_change_link = True
    extra = 0


@admin.register(production_logs.ProductionLog)
class ProductionLogAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'name']
    inlines = [ProductionLogEntryInline]
    fieldsets = (
        (None, {'fields': ['film', 'name', 'start_date', 'user', 'storage_backend']},),
        ('Summary', {'fields': ['summary', 'author', 'picture_16_9', 'youtube_link']}),
    )
