"""Serializers for training API."""
import common.serializers
import training.models.sections


class TrainingSerializer(common.serializers.IdModelSerializer):
    """Serialize a Training."""

    class Meta:
        model = training.models.trainings.Training
        fields = '__all__'


class SectionSerializer(common.serializers.IdModelSerializer):
    """Serialize a training Section."""

    class Meta:
        model = training.models.sections.Section
        fields = '__all__'
        writable_fields = (
            'is_featured',
            'is_free',
            'is_published',
            'name',
            'preview_youtube_link',
            'static_asset_id',
        )
        raw_id_fields = ['static_asset_id']
        labels = {
            'static_asset_id': 'Static asset ID',
            'preview_youtube_link': 'Preview YouTube link',
        }
