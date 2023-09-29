"""Commonly used API serializers."""
from django.conf import settings
from django.urls.base import reverse
from rest_framework import relations
from rest_framework import serializers


def make_absolute_url(url: str) -> str:
    """Turn a host-absolute URL into a fully absolute URL.

    For simplicity, assumes we're using HTTPS, unless in DEBUG mode,
    and not running on some URL prefix.
    """
    from django.contrib.sites.models import Site
    from urllib.parse import urljoin

    site: Site = Site.objects.get_current()
    return urljoin(f'http{not settings.DEBUG and "s" or ""}://{site.domain}/', url)


class IdManyRelatedField(serializers.ManyRelatedField):
    """Append an "_ids" suffix to names of m2m related fields."""

    field_name_suffix = '_ids'

    def bind(self, field_name, parent):
        """Bind the field is bound to the serializer.

        Changes the source so that the original field name is used
        (removes the "_ids" suffix).
        """
        self.source = field_name[: -len(self.field_name_suffix)]
        super().bind(field_name, parent)


class IdPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Append an "_id" suffix to names of related fields.

    Only works together the IdModelSerializer.
    """

    many_related_field_class = IdManyRelatedField
    field_name_suffix = '_id'

    @classmethod
    def many_init(cls, *args, **kwargs):  # noqa: D102
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs:
            if key in relations.MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return cls.many_related_field_class(**list_kwargs)

    def bind(self, field_name, parent):
        """Bind the field is bound to the serializer.

        Changes the source so that the original field name is used
        (removes the "_id" suffix).
        """
        if field_name:
            self.source = field_name[: -len(self.field_name_suffix)]
        super().bind(field_name, parent)


class IdModelSerializer(serializers.ModelSerializer):
    """Change field names of related fields to FIELD_NAME_id/_ids."""

    serializer_related_field = IdPrimaryKeyRelatedField

    admin_url = serializers.SerializerMethodField()
    view_on_site_url = serializers.SerializerMethodField()

    def get_admin_url(self, obj):
        """Return an absolute admin URL of the object."""
        url_name = f'admin:{obj._meta.app_label}_{obj.__class__.__name__.lower()}_change'
        return make_absolute_url(reverse(url_name, args=[obj.pk]))

    def get_view_on_site_url(self, obj):
        """Return an absolute URL to the objects on the Studio website."""
        obj_url = None
        if hasattr(obj, 'get_absolute_url'):
            obj_url = obj.get_absolute_url()
        elif hasattr(obj, 'url'):
            obj_url = obj.url
        if not obj_url:
            return None
        return make_absolute_url(obj_url)

    def get_fields(self):  # noqa: D102
        fields = super().get_fields()
        new_fields = type(fields)()

        for field_name, field in fields.items():
            try:
                field_name += field.field_name_suffix
            except AttributeError:
                pass
            new_fields[field_name] = field
        return new_fields

    def __init__(self, *args, **kwargs):
        """Set some field flags in bulk, override some widgets in API docs.

        Handles the following new Meta attributes:

        writable_fields: list of writable field names
        raw_id_fields: list, overrides heavy selects with simple inputs in API docs
        labels: dict, overrides field labels in API docs
        """
        super().__init__(*args, **kwargs)
        meta = self.__class__.Meta
        for field in self.fields:
            if hasattr(meta, 'writable_fields') and field not in meta.writable_fields:
                self.fields[field].read_only = True
            if hasattr(meta, 'labels') and field in meta.labels:
                self.fields[field].label = meta.labels[field]
            # Prevent DRF from attempting to render inputs from all of the related model choices
            if hasattr(meta, 'raw_id_fields') and field in meta.raw_id_fields:
                self.fields[field].style = {'base_template': 'input.html'}
