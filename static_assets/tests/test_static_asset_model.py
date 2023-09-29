from unittest.mock import patch, call, Mock
import datetime
import mimetypes

from django.test import TestCase

from common.tests.factories.static_assets import (
    StaticAssetFactory,
    VideoVariationFactory,
)
from common.tests.factories.users import UserFactory
from static_assets.models import StaticAsset, Video


class TestStaticAssetModel(TestCase):
    @patch('storages.backends.s3boto3.S3Boto3Storage.url', return_value='s3://file')
    def test_static_asset_storage_urls(self, mock_storage_url):
        """Tests for the StaticAsset file fields.

        Create a new static asset and check that the right storage is called when its file URLs are accessed.
        """
        asset: StaticAsset = StaticAssetFactory()

        self.assertEqual(asset.source.url, 's3://file')
        self.assertEqual(asset.thumbnail.url, 's3://file')

        mock_storage_url.assert_has_calls((call(asset.source.name), call(asset.thumbnail.name)))

    @patch('storages.backends.s3boto3.S3Boto3Storage.url', return_value='s3://file')
    def test_video_duration_label(self, mock_storage_url):

        video: Video = StaticAssetFactory(source_type='video').video

        video.duration = datetime.timedelta(seconds=10)
        self.assertEqual(video.duration_label, '0:10')

        video.duration = datetime.timedelta(minutes=1, seconds=10)
        self.assertEqual(video.duration_label, '1:10')

        video.duration = datetime.timedelta(minutes=10, seconds=10)
        self.assertEqual(video.duration_label, '10:10')

        video.duration = datetime.timedelta(hours=1, minutes=10, seconds=1)
        self.assertEqual(video.duration_label, '1:10:01')

        video.duration = datetime.timedelta(hours=1, minutes=1, seconds=1)
        self.assertEqual(video.duration_label, '1:01:01')

    def test_content_type(self):
        """Test that StaticAsset app adds/overwrites some mimetypes."""
        content_type, _ = mimetypes.guess_type('test.blend')
        self.assertEqual(content_type, 'application/x-blender')

        content_type, _ = mimetypes.guess_type('test.exr')
        self.assertEqual(content_type, 'application/x-exr')

        content_type, _ = mimetypes.guess_type('test.hdr')
        self.assertEqual(content_type, 'application/x-radiance-hdr')

        content_type, _ = mimetypes.guess_type('test.kra')
        self.assertEqual(content_type, 'application/x-krita')

        content_type, _ = mimetypes.guess_type('test.wav')
        self.assertEqual(content_type, 'audio/wav')

        content_type, _ = mimetypes.guess_type('test.mp4')
        self.assertEqual(content_type, 'video/mp4')

        content_type, _ = mimetypes.guess_type('test.m4v')
        self.assertEqual(content_type, 'video/mp4')

        content_type, _ = mimetypes.guess_type('test.png')
        self.assertEqual(content_type, 'image/png')

        content_type, _ = mimetypes.guess_type('test.jpg')
        self.assertEqual(content_type, 'image/jpeg')

    @patch('static_assets.views.is_free_static_asset', Mock(return_value=True))
    def test_static_asset_source_used_in_download_url(self):
        video = StaticAssetFactory(source_type='video', source='path/to/original-video.mp4').video

        self.assertEqual(video.static_asset.source.name, 'path/to/original-video.mp4')
        self.assertIsNone(video.default_variation)
        self.assertIsNotNone(video.static_asset.source.name)
        self.assertEqual(
            video.static_asset.download_url, '/download-source/path/to/original-video.mp4',
        )

        # Check that this URL redirects to storage/CDN, as expected
        self.client.force_login(UserFactory())
        res = self.client.get(video.static_asset.download_url)
        self.assertEqual(res.status_code, 302)
        self.assertTrue('path/to/original-video.mp4' in res['Location'])
        self.assertFalse('login' in res['Location'])

    @patch('static_assets.views.is_free_static_asset', Mock(return_value=True))
    def test_no_source_video_variation_source_used_in_download_url(self):
        video_variation = VideoVariationFactory(
            source='path/to/video-variation-1080p.mp4',
            video=StaticAssetFactory(source_type='video', source=None).video,
        )

        self.assertEqual(video_variation.source.name, 'path/to/video-variation-1080p.mp4')
        self.assertEqual(
            video_variation.video.static_asset.download_source.name,
            'path/to/video-variation-1080p.mp4',
        )
        self.assertIsNotNone(video_variation.video.default_variation)
        self.assertIsNone(video_variation.video.static_asset.source.name)
        self.assertEqual(
            video_variation.video.static_asset.download_url,
            '/download-source/path/to/video-variation-1080p.mp4',
        )

        # Check that this URL redirects to storage/CDN, as expected
        self.client.force_login(UserFactory())
        res = self.client.get(video_variation.video.static_asset.download_url)
        self.assertEqual(res.status_code, 302)
        self.assertTrue('path/to/video-variation-1080p.mp4' in res['Location'])
        self.assertFalse('login' in res['Location'])
