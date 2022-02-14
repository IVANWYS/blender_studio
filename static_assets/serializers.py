"""Serializers for static asset API."""
from rest_framework import serializers
from django.core.files import storage

from static_assets.models import License, StaticAsset
import common.serializers


class UploadSerializer(serializers.Serializer):
    """Serialise payload of the Get upload URL endpoint."""

    original_filename = serializers.CharField(required=True)

    url = serializers.URLField(read_only=True)
    fields = serializers.DictField(read_only=True)


def _validate_existing_storage_path(value: str) -> str:
    if not storage.default_storage.exists(value):
        raise serializers.ValidationError('Must point to an existing file')
    return value


class LicenseSerializer(serializers.ModelSerializer):
    """Serialiase License."""

    class Meta:
        model = License
        fields = '__all__'


class StaticAssetSerializer(common.serializers.IdModelSerializer):
    """Serialise StaticAsset."""

    class Meta:
        model = StaticAsset
        fields = '__all__'
        writable_fields = (
            'author_id',
            'contributors_ids',
            'license_id',
            'source_path',
            'thumbnail_path',
        )
        raw_id_fields = ('author_id', 'contributors_ids')
        labels = {
            'author_id': 'Author ID',
            'contributors_ids': 'Contributors IDs',
            'license_id': 'License ID',
        }

    license_id = serializers.IntegerField(required=False)
    license = LicenseSerializer()
    source_path = serializers.CharField(
        source='source', help_text='Path to a source file that already exists in storage.',
    )
    thumbnail_path = serializers.CharField(
        source='thumbnail',
        required=False,
        help_text='Path to a thumbnail file that already exists in storage.',
    )

    def validate_source_path(self, value):
        """Validate given source_path."""
        return _validate_existing_storage_path(value)

    def validate_thumbnail_path(self, value):
        """Validate given thumbnail_path."""
        return _validate_existing_storage_path(value)
