from unittest.mock import MagicMock, Mock, patch, PropertyMock
import factory
import random
from factory import fuzzy
from factory.django import DjangoModelFactory

from common.tests.factories.helpers import generate_file_path
from common.tests.factories.users import UserFactory
from static_assets.models import (
    License,
    StaticAsset,
    StaticAssetFileTypeChoices,
    VideoVariation,
)

mock_file = MagicMock()
# Since "name" is an argument to the Mock constructor,
# a "name" attribute can't just be passed at creation time inside a patch call.
mock_file.configure_mock(name='OriginalMockFileName.mp4')


class LicenseFactory(DjangoModelFactory):
    class Meta:
        model = License

    name = factory.Faker('text', max_nb_chars=15)
    slug = factory.Faker('slug')
    description = factory.Faker('text')
    url = factory.Faker('url')


class StaticAssetFactory(DjangoModelFactory):
    class Meta:
        model = StaticAsset

    @classmethod
    def _create(cls, *args, **kwargs):
        with patch('django.core.files.storage.Storage.open', Mock(return_value=mock_file)), patch(
            'django.core.files.storage.default_storage.exists', Mock(return_value=True)
        ), patch(
            'django.db.models.fields.files.FieldFile.size', PropertyMock(return_value=1048576)
        ):
            return super(StaticAssetFactory, cls)._create(*args, **kwargs)

    # TODO: Generate realistic names, based on file type
    original_filename = "original_name.mp4"
    source = factory.LazyFunction(generate_file_path)
    source_type = fuzzy.FuzzyChoice(StaticAssetFileTypeChoices, getter=lambda c: c.value)
    size_bytes = 1048576
    user = factory.SubFactory(UserFactory)
    license = factory.SubFactory(LicenseFactory)
    thumbnail = factory.LazyFunction(generate_file_path)


class VideoVariationFactory(DjangoModelFactory):
    class Meta:
        model = VideoVariation

    size_bytes = factory.LazyFunction(lambda: random.randint(0, 100 ** 3))
    resolution_label = '720p'
    source = factory.LazyFunction(generate_file_path)
