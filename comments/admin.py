from django.contrib import admin
from django.db.models import QuerySet
from django.db.models import Value, Case, When, Exists, OuterRef, Q
from django.db.models.fields import BooleanField
from django.http.request import HttpRequest

from comments import models
from common.mixins import AdminUserDefaultMixin
from common.types import assert_cast


@admin.register(models.Comment)
class CommentAdmin(AdminUserDefaultMixin, admin.ModelAdmin):
    list_display = ['__str__', 'comment_under', 'has_replies', 'is_deleted']
    list_filter = ['user', 'date_created', 'date_deleted']

    def get_queryset(self, request: HttpRequest) -> 'QuerySet[models.Comment]':
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _comment_under=Case(
                When(section__isnull=False, then='section__name'),
                When(asset__isnull=False, then='asset__name'),
                default=Value(''),
            ),
            _has_replies=Exists(models.Comment.objects.filter(reply_to_id=OuterRef('pk'))),
            _is_deleted=Case(
                When(date_deleted__isnull=False, then=Value(True)),
                default=False,
                output_field=BooleanField(),
            ),
        )
        return queryset

    def comment_under(self, obj: models.Comment) -> str:
        return assert_cast(str, getattr(obj, '_comment_under'))

    def has_replies(self, obj: models.Comment) -> bool:
        return assert_cast(bool, getattr(obj, '_has_replies'))

    def is_deleted(self, obj: models.Comment) -> bool:
        return assert_cast(bool, getattr(obj, '_is_deleted'))
