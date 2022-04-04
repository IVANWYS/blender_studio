from django.contrib import admin

from .models import TemplateVariable


@admin.register(TemplateVariable)
class TemplateVariableAdmin(admin.ModelAdmin):
    list_display = ('key', 'text', 'image')
