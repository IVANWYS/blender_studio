from unittest.mock import patch, Mock

from django.test import TestCase

from looper.tests.test_preferred_currency import EURO_IPV4, USA_IPV4

from common.tests.factories.characters import CharacterVersionFactory, CharacterShowcaseFactory
from common.tests.factories.subscriptions import SubscriptionFactory
from common.tests.factories.users import UserFactory
from stats.models import StaticAssetView


@patch('sorl.thumbnail.base.ThumbnailBackend.get_thumbnail', Mock(url=''))
class TestCharacterVersion(TestCase):
    def test_get_records_a_static_asset_view(self):
        version = CharacterVersionFactory(is_published=True, character__is_published=True)
        self.assertEqual(0, StaticAssetView.objects.count())
        url = version.get_absolute_url()

        # "View" the character version anonymously
        response = self.client.get(url, REMOTE_ADDR=USA_IPV4)

        # A record of this view should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, StaticAssetView.objects.count())
        view = StaticAssetView.objects.first()
        self.assertEqual(view.static_asset_id, version.static_asset_id)
        self.assertEqual(view.ip_address, USA_IPV4)
        self.assertIsNone(view.user_id)

        # "View" the character version anonymously again, from the same IP
        response = self.client.get(url, REMOTE_ADDR=USA_IPV4)

        # No new records should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1, StaticAssetView.objects.count(), [_ for _ in StaticAssetView.objects.all()]
        )

        # "View" the character version anonymously, from another IP
        response = self.client.get(url, REMOTE_ADDR=EURO_IPV4)

        # A record of this view should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, StaticAssetView.objects.count())
        self.assertEqual(
            StaticAssetView.objects.get(ip_address=EURO_IPV4).static_asset_id,
            version.static_asset_id,
        )

        # "View" the character version as logged in user, IP doesn't matter
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(url, REMOTE_ADDR=EURO_IPV4)

        # A record of this view should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, StaticAssetView.objects.count())
        self.assertEqual(
            StaticAssetView.objects.get(user_id=user.pk).static_asset_id, version.static_asset_id
        )

        # "View" the character version as logged in user, same user, IP doesn't matter
        self.client.force_login(user)
        response = self.client.get(url, REMOTE_ADDR=USA_IPV4)

        # No new records should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, StaticAssetView.objects.count())

        # "View" the character version as logged in user, different user, IP doesn't matter
        another_user = UserFactory()
        self.client.force_login(another_user)
        response = self.client.get(url, REMOTE_ADDR=EURO_IPV4)

        # A record of this view should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(4, StaticAssetView.objects.count())
        self.assertEqual(
            StaticAssetView.objects.get(user_id=another_user.pk).static_asset_id,
            version.static_asset_id,
        )


@patch('sorl.thumbnail.base.ThumbnailBackend.get_thumbnail', Mock(url=''))
class TestCharacterShowcase(TestCase):
    def test_get_records_a_static_asset_view(self):
        showcase = CharacterShowcaseFactory(is_published=True, character__is_published=True)
        self.assertEqual(0, StaticAssetView.objects.count())
        url = showcase.get_absolute_url()

        # "View" the character showcase anonymously
        response = self.client.get(url, REMOTE_ADDR=USA_IPV4)

        # A record of this view should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, StaticAssetView.objects.count())
        view = StaticAssetView.objects.first()
        self.assertEqual(view.static_asset_id, showcase.static_asset_id)
        self.assertEqual(view.ip_address, USA_IPV4)
        self.assertIsNone(view.user_id)

        # "View" the character showcase anonymously again, from the same IP
        response = self.client.get(url, REMOTE_ADDR=USA_IPV4)

        # No new records should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            1, StaticAssetView.objects.count(), [_ for _ in StaticAssetView.objects.all()]
        )

        # "View" the character showcase anonymously, from another IP
        response = self.client.get(url, REMOTE_ADDR=EURO_IPV4)

        # A record of this view should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, StaticAssetView.objects.count())
        self.assertEqual(
            StaticAssetView.objects.get(ip_address=EURO_IPV4).static_asset_id,
            showcase.static_asset_id,
        )

        # "View" the character showcase as logged in user, IP doesn't matter
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(url, REMOTE_ADDR=EURO_IPV4)

        # A record of this view should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, StaticAssetView.objects.count())
        self.assertEqual(
            StaticAssetView.objects.get(user_id=user.pk).static_asset_id, showcase.static_asset_id
        )

        # "View" the character showcase as logged in user, same user, IP doesn't matter
        self.client.force_login(user)
        response = self.client.get(url, REMOTE_ADDR=USA_IPV4)

        # No new records should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, StaticAssetView.objects.count())

        # "View" the character showcase as logged in user, different user, IP doesn't matter
        another_user = UserFactory()
        self.client.force_login(another_user)
        response = self.client.get(url, REMOTE_ADDR=EURO_IPV4)

        # A record of this view should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(4, StaticAssetView.objects.count())
        self.assertEqual(
            StaticAssetView.objects.get(user_id=another_user.pk).static_asset_id,
            showcase.static_asset_id,
        )


@patch('storages.backends.s3boto3.S3Boto3Storage.url', Mock(return_value='https://bucket/file'))
class TestCharacterVersionDownload(TestCase):
    def test_cannot_download_non_free_when_anonymous(self):
        character_version = CharacterVersionFactory(is_free=False)

        response = self.client.get(character_version.static_asset.download_url)

        self.assertEqual(response.status_code, 404)

    def test_cannot_download_non_free_when_not_subscribed(self):
        user = UserFactory()
        character_version = CharacterVersionFactory(is_free=False)

        self.client.force_login(user)
        response = self.client.get(character_version.static_asset.download_url)

        self.assertEqual(response.status_code, 404)

    def test_can_download_non_free_when_subscribed(self):
        user = UserFactory()
        SubscriptionFactory(user=user, status='active')
        character_version = CharacterVersionFactory(is_free=False)

        self.client.force_login(user)
        response = self.client.get(character_version.static_asset.download_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://bucket/file')

    def test_can_download_free_when_anonymous(self):
        character_version = CharacterVersionFactory(is_free=True)

        response = self.client.get(character_version.static_asset.download_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://bucket/file')

    def test_can_download_free_when_not_subscribed(self):
        user = UserFactory()
        character_version = CharacterVersionFactory(is_free=True)

        self.client.force_login(user)
        response = self.client.get(character_version.static_asset.download_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://bucket/file')


@patch('storages.backends.s3boto3.S3Boto3Storage.url', Mock(return_value='https://bucket/file'))
class TestCharacterShowcaseDownload(TestCase):
    def test_cannot_download_non_free_when_anonymous(self):
        character_showcase = CharacterShowcaseFactory(is_free=False)

        response = self.client.get(character_showcase.static_asset.download_url)

        self.assertEqual(response.status_code, 404)

    def test_cannot_download_non_free_when_not_subscribed(self):
        user = UserFactory()
        character_showcase = CharacterShowcaseFactory(is_free=False)

        self.client.force_login(user)
        response = self.client.get(character_showcase.static_asset.download_url)

        self.assertEqual(response.status_code, 404)

    def test_can_download_non_free_when_subscribed(self):
        user = UserFactory()
        SubscriptionFactory(user=user, status='active')
        character_showcase = CharacterShowcaseFactory(is_free=False)

        self.client.force_login(user)
        response = self.client.get(character_showcase.static_asset.download_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://bucket/file')

    def test_can_download_free_when_anonymous(self):
        character_showcase = CharacterShowcaseFactory(is_free=True)

        response = self.client.get(character_showcase.static_asset.download_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://bucket/file')

    def test_can_download_free_when_not_subscribed(self):
        user = UserFactory()
        character_showcase = CharacterShowcaseFactory(is_free=True)

        self.client.force_login(user)
        response = self.client.get(character_showcase.static_asset.download_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://bucket/file')
