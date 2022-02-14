"""Commonly used model and admin mixins."""
from functools import lru_cache
from typing import Optional, Any, Union, List, Tuple
import logging

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.db.models.base import Model
from django.http.request import HttpRequest
from django.utils.safestring import mark_safe

import looper.model_mixins
import looper.admin_log

from sorl.thumbnail import get_thumbnail

log = logging.getLogger(__name__)


class CreatedUpdatedMixin(models.Model):
    """Add standard date fields to a model."""

    class Meta:
        abstract = True

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class AdminUserDefaultMixin:
    """On object creation, sets the 'user' field in the form in Admin to the current user.

    The field value will be displayed as read-only in the form.
    """

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)  # type: ignore[call-arg]
        assert issubclass(
            cls, admin.options.BaseModelAdmin
        ), f'{cls.__name__} has to be a subclass of BaseModelAdmin to use the UserDefaultMixin'

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[Model] = None
    ) -> Union[List[str], Tuple[str]]:
        """Display (non-editable) user field in the form"""
        readonly_fields = ['user', *super().get_readonly_fields(request, obj)]
        return readonly_fields

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        """Associate created object with the current user."""
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request: Any, form: Any, formset: Any, change: Any) -> None:
        """Associate created object with the current user: handle inline forms."""
        for form in formset.forms:
            if not getattr(form, 'instance', None):
                continue
            if form.instance.pk:
                # Changing, not adding
                continue
            if hasattr(form.instance, 'user_id') and not form.instance.user_id:
                form.instance.user = request.user
        super().save_formset(request, form, formset, change)


class ViewOnSiteMixin:
    """Add `view_link` attribute to model admin."""

    def view_link(self, obj):
        """Render a link to a given object."""
        if getattr(obj, 'get_absolute_url', None) and obj.get_absolute_url():
            return mark_safe(
                '<a href="{0}" target="_blank">{1}</a>'.format(
                    obj.get_absolute_url(), "View on site"
                )
            )
        return '-'

    view_link.allow_tags = True
    view_link.short_description = "View on site"


@lru_cache(maxsize=1024)
def _cacheable_get_thumnbnail(thumbnail, size_settings):
    return get_thumbnail(thumbnail, size_settings, crop=settings.THUMBNAIL_CROP_MODE).url


class StaticThumbnailURLMixin:
    """Add `thumbnail_<size>_url` properties generating static cacheable thumbnail URLs."""

    thumbnail = None  # Is always overridden

    def _get_thumbnail(self, size_settings):
        if not self.thumbnail:
            return None
        try:
            return _cacheable_get_thumnbnail(self.thumbnail, size_settings)
        except OSError as e:
            # Handle the classic 'cannot write mode RGBA as JPEG'
            log.error(e)
            return None

    @property
    def thumbnail_m_url(self) -> Optional[str]:
        """Return a static URL to a medium-sized thumbnail."""
        return self._get_thumbnail(settings.THUMBNAIL_SIZE_M)

    @property
    def thumbnail_s_url(self) -> Optional[str]:
        """Return a static URL to a small thumbnail."""
        return self._get_thumbnail(settings.THUMBNAIL_SIZE_S)


class ThumbnailMixin:
    """Display an asset thumbnail, if available."""

    def view_thumbnail(self, obj):
        """Return an img tag with an asset thumbnail, if available."""
        static_asset = getattr(obj, 'static_asset', obj)
        img_url = getattr(static_asset, 'thumbnail_s_url', None)
        if img_url:
            return mark_safe(f'<img width=100 src="{img_url}">')
        return ''

    view_thumbnail.allow_tags = True


class SaveAndRecordChangesMixin:
    """Save and record changes happening to record_modification_fields."""

    def save_and_record_changes(self, *args, **kwargs):
        """Add a LogEntry if any of record_modification_fields have changed."""
        was_changed, old_state = self.pre_save_record()

        super().save(*args, **kwargs)

        if self.pk is None:  # not logging changed when newly created
            return
        if not was_changed:
            return

        msgs = []
        for field in self.record_modification_fields:
            if field not in old_state:
                continue
            old_value = old_state[field]
            new_value = getattr(self, field)
            if old_value == new_value:
                continue
            msgs.append(f'Changed: "{field}" from "{old_value}" to "{new_value}"')
        if not msgs:
            return
        user_id = None
        if getattr(self, '_modified_by_user_id', None):
            user_id = self._modified_by_user_id
            # Unset the attribute in case this object happens to be reused between requests.
            delattr(self, '_modified_by_user_id')
        try:
            looper.admin_log.attach_log_entry(self, '\n'.join(msgs), user_id=user_id)
        except Exception:
            log.exception('Unable to record change')


class SetModifiedByViewMixin:
    """Set a _modified_by_user_id attribute on an object retrieved by the API."""

    def get_object(self, *args, **kwargs):  # noqa: 155
        obj = super().get_object(*args, **kwargs)
        obj._modified_by_user_id = self.request.user.pk
        return obj
