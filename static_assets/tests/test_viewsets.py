from unittest.mock import patch, Mock, PropertyMock, MagicMock

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse_lazy
from freezegun import freeze_time

from looper import admin_log

from common.tests.factories.static_assets import StaticAssetFactory, LicenseFactory
from common.tests.factories.users import UserFactory
from static_assets.models import StaticAsset

mock_file = MagicMock()
# Since "name" is an argument to the Mock constructor,
# a "name" attribute can't just be passed at creation time inside a patch call.
mock_file.configure_mock(name='test-file2.mp4')


class UploadViewSetTest(TestCase):
    url = reverse_lazy('api:upload-list')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.staff_user = UserFactory(is_staff=True)

    def test_get_not_allowed_anonymous(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_get_not_allowed_as_non_staff(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_get_not_allowed_as_staff(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)

    def test_post_anonymous_denied(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 401)

    def test_post_as_non_staff_denied(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 403)

    def test_post_as_staff_without_relevant_permissions_denied(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 403)

    def test_post_as_staff_with_permissions_validation_error_original_filename_required(self):
        self.client.force_login(self.staff_user)
        permission = Permission.objects.get(codename='add_staticasset')
        self.staff_user.user_permissions.add(permission)

        response = self.client.post(self.url, data={}, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {'original_filename': ['This field is required.']})

    @patch(
        'static_assets.viewsets.get_upload_to_hashed_path',
        Mock(return_value='foo/bar/test-file.mp4'),
    )
    def test_post_as_staff_with_permissions_returns_upload_url_and_fields(self):
        self.client.force_login(self.staff_user)
        permission = Permission.objects.get(codename='add_staticasset')
        self.staff_user.user_permissions.add(permission)

        data = {'original_filename': 'my_file.mp4'}
        response = self.client.post(self.url, data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json['url'], 'https://blender-studio-test.s3.amazonaws.com/')
        self.assertEqual(response_json['original_filename'], 'my_file.mp4')
        self.assertEqual(
            sorted(response_json['fields'].keys()),
            [
                'key',
                'policy',
                'x-amz-algorithm',
                'x-amz-credential',
                'x-amz-date',
                'x-amz-signature',
            ],
            response_json['fields'],
        )
        self.assertEqual(response_json['fields']['key'], 'foo/bar/test-file.mp4')


@freeze_time('2022-02-08T18:12:20+01:00')
@patch('storages.backends.s3boto3.S3Boto3Storage.url', Mock(return_value='https://bucket/file'))
@patch('django.core.files.storage.Storage.open', Mock(return_value=mock_file))
@patch('django.db.models.fields.files.FieldFile.size', PropertyMock(return_value=99999))
class StaticAssetsViewSetTestCase(TestCase):
    maxDiff = None
    list_url = reverse_lazy('api:staticasset-list')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.staff_user = UserFactory(is_staff=True)
        cls.default_license = LicenseFactory(
            slug='cc-by',
            name='CC-BY',
            url='https://example.com',
            description='Description of CC-BY',
        )
        # because patch doesn't cover setUp,
        # this is called by each task that needs an pre-existing static asset
        cls.static_asset = StaticAssetFactory(
            user_id=cls.staff_user.id,
            source_type='video',
            source='foo/bar/test-file.mp4',
            thumbnail='foo/bar/test-file.png',
            license_id=cls.default_license.id,
        )
        cls.detail_url = reverse_lazy('api:staticasset-detail', kwargs={'pk': cls.static_asset.id})

    def test_list_anonymous_denied(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 401)

    def test_list_as_non_staff_denied(self):
        self.client.force_login(self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)

    def test_list_as_staff(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'count': 1,
                'next': None,
                'previous': None,
                'results': [
                    {
                        'author_id': None,
                        'content_type': 'video/mp4',
                        'contributors_ids': [],
                        'date_created': '2022-02-08T18:12:20+01:00',
                        'date_updated': '2022-02-08T18:12:20+01:00',
                        'download_count': 0,
                        'id': self.static_asset.id,
                        'license_id': self.default_license.id,
                        'license': {
                            'description': 'Description of CC-BY',
                            'id': self.default_license.id,
                            'name': 'CC-BY',
                            'slug': 'cc-by',
                            'url': 'https://example.com',
                        },
                        'original_filename': 'OriginalMockFileName.mp4',
                        'size_bytes': 1048576,
                        'slug': '',
                        'source': 'https://bucket/file',
                        'source_path': 'foo/bar/test-file.mp4',
                        'source_type': 'video',
                        'thumbnail': 'https://bucket/file',
                        'thumbnail_path': 'foo/bar/test-file.png',
                        'user_id': self.staff_user.id,
                        'view_count': 0,
                    }
                ],
            },
        )

    def test_retrieve_anonymous_denied(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 401)

    def test_retrieve_as_non_staff_denied(self):
        self.client.force_login(self.user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 403)

    def test_retrieve_as_staff(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                'author_id': None,
                'content_type': 'video/mp4',
                'contributors_ids': [],
                'date_created': '2022-02-08T18:12:20+01:00',
                'date_updated': '2022-02-08T18:12:20+01:00',
                'download_count': 0,
                'id': self.static_asset.id,
                'license_id': self.default_license.id,
                'license': {
                    'description': 'Description of CC-BY',
                    'id': self.default_license.id,
                    'name': 'CC-BY',
                    'slug': 'cc-by',
                    'url': 'https://example.com',
                },
                'original_filename': 'OriginalMockFileName.mp4',
                'size_bytes': 1048576,
                'slug': '',
                'source': 'https://bucket/file',
                'source_path': 'foo/bar/test-file.mp4',
                'source_type': 'video',
                'thumbnail': 'https://bucket/file',
                'thumbnail_path': 'foo/bar/test-file.png',
                'user_id': self.staff_user.id,
                'view_count': 0,
            },
        )

    def test_create_anonymous_denied(self):
        response = self.client.post(self.list_url, {})

        self.assertEqual(response.status_code, 401)

    def test_create_as_non_staff_denied(self):
        self.client.force_login(self.user)

        response = self.client.post(self.list_url, {})

        self.assertEqual(response.status_code, 403)

    def test_create_as_staff_without_permissions_denied(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(self.list_url, {})

        self.assertEqual(response.status_code, 403)

    def test_create_as_staff_with_permissions_validation_errors_invalid_path(self):
        self.client.force_login(self.staff_user)
        permission = Permission.objects.get(codename='add_staticasset')
        self.staff_user.user_permissions.add(permission)

        response = self.client.post(
            self.list_url,
            {'source_path': 'foo/bar/test-file.mp4', 'thumbnail_path': 'foo/bar/test-file.png'},
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json(),
            {
                'source_path': ['Must point to an existing file'],
                'thumbnail_path': ['Must point to an existing file'],
            },
        )

    @patch('django.core.files.storage.default_storage.exists', Mock(return_value=True))
    def test_create_as_staff_with_permissions(self):
        self.client.force_login(self.staff_user)
        permission = Permission.objects.get(codename='add_staticasset')
        self.staff_user.user_permissions.add(permission)
        self.assertEqual(StaticAsset.objects.count(), 1)

        data = {
            'source_path': 'foo/bar/new-test-file.mp4',
            'thumbnail_path': 'foo/bar/new-test-file.png',
        }
        response = self.client.post(self.list_url, data, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(StaticAsset.objects.count(), 2)
        static_asset = StaticAsset.objects.get(source__contains='new-test-file')
        self.assertNotEqual(self.static_asset.id, static_asset.id)
        self.assertDictEqual(
            response.json(),
            {
                'author_id': None,
                'content_type': 'video/mp4',
                'contributors_ids': [],
                'date_created': '2022-02-08T18:12:20+01:00',
                'date_updated': '2022-02-08T18:12:20+01:00',
                'download_count': 0,
                'id': static_asset.id,
                'license_id': self.default_license.id,
                'license': {
                    'description': 'Description of CC-BY',
                    'id': self.default_license.id,
                    'name': 'CC-BY',
                    'slug': 'cc-by',
                    'url': 'https://example.com',
                },
                'original_filename': 'test-file2.mp4',
                'size_bytes': 99999,
                'slug': '',
                'source': 'https://bucket/file',
                'source_path': 'foo/bar/new-test-file.mp4',
                'source_type': 'video',
                'thumbnail': 'https://bucket/file',
                'thumbnail_path': 'foo/bar/new-test-file.png',
                'user_id': self.staff_user.id,
                'view_count': 0,
            },
        )

    def test_update_as_staff_with_permissions_change_license(self):
        self.client.force_login(self.staff_user)
        permissions = Permission.objects.filter(codename__in={'change_staticasset'})
        self.staff_user.user_permissions.add(*permissions)

        old_license = self.static_asset.license
        new_license = LicenseFactory(
            slug='cc-by',
            name='CC-BY',
            url='https://example.com',
            description='Description of CC-BY',
        )
        data = {'license_id': new_license.id}
        response = self.client.patch(self.detail_url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.static_asset.refresh_from_db()
        self.assertNotEqual(self.static_asset.license_id, old_license.id)
        self.assertEqual(self.static_asset.license_id, new_license.id)
        self.assertDictEqual(
            response.json()['license'],
            {
                'description': 'Description of CC-BY',
                'id': new_license.id,
                'name': 'CC-BY',
                'slug': 'cc-by',
                'url': 'https://example.com',
            },
        )

    def test_update_as_staff_with_permissions_set_contributors(self):
        self.client.force_login(self.staff_user)
        permissions = Permission.objects.filter(codename__in={'change_staticasset'})
        self.staff_user.user_permissions.add(*permissions)

        contributors_ids = [UserFactory().id for _ in range(2)]
        # create some more users, who aren't contributors
        [UserFactory().id for _ in range(3)]
        data = {'contributors_ids': contributors_ids}
        response = self.client.patch(self.detail_url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.static_asset.refresh_from_db()
        self.assertEqual(
            sorted([_.id for _ in self.static_asset.contributors.all()]), contributors_ids,
        )
        self.assertEqual(response.json()['contributors_ids'], contributors_ids)

    @patch('django.core.files.storage.default_storage.exists', Mock(return_value=True))
    def test_update_as_staff_with_permissions_set_source_path(self):
        self.client.force_login(self.staff_user)
        permissions = Permission.objects.filter(codename__in={'change_staticasset'})
        self.staff_user.user_permissions.add(*permissions)
        old_source = self.static_asset.source

        data = {'source_path': 'new/source/path/file.mp4'}
        response = self.client.patch(self.detail_url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.static_asset.refresh_from_db()
        self.assertNotEqual(old_source, self.static_asset.source)
        self.assertEqual(self.static_asset.source.name, 'new/source/path/file.mp4')
        self.assertEqual(response.json()['source_path'], 'new/source/path/file.mp4')
        entries_q = admin_log.entries_for(self.static_asset)
        self.assertEqual(entries_q.count(), 1)
        self.assertEqual(
            entries_q.first().change_message,
            f'Changed: "source" from "{old_source}" to "new/source/path/file.mp4"',
        )
        self.assertEqual(entries_q.first().user_id, self.staff_user.id)

    @patch('django.core.files.storage.default_storage.exists', Mock(return_value=True))
    def test_update_as_staff_with_permissions_set_thumbnail_path(self):
        self.client.force_login(self.staff_user)
        permissions = Permission.objects.filter(codename__in={'change_staticasset'})
        self.staff_user.user_permissions.add(*permissions)
        old_thumbnail = self.static_asset.thumbnail

        data = {'thumbnail_path': 'new/source/path/file.png'}
        response = self.client.patch(self.detail_url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.static_asset.refresh_from_db()
        self.assertNotEqual(old_thumbnail, self.static_asset.thumbnail)
        self.assertEqual(self.static_asset.thumbnail.name, 'new/source/path/file.png')
        self.assertEqual(response.json()['thumbnail_path'], 'new/source/path/file.png')
        entries_q = admin_log.entries_for(self.static_asset)
        self.assertEqual(entries_q.count(), 1)
        self.assertEqual(
            entries_q.first().change_message,
            f'Changed: "thumbnail" from "{old_thumbnail}" to "new/source/path/file.png"',
        )
        self.assertEqual(entries_q.first().user_id, self.staff_user.id)

    def test_delete_as_anonymous_denied(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 401)

    def test_delete_as_non_staff_denied(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)

    def test_delete_as_staff_without_permissions(self):
        self.client.force_login(self.staff_user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)

    def test_delete_as_staff_with_permissions(self):
        self.client.force_login(self.staff_user)
        permissions = Permission.objects.filter(codename__in={'delete_staticasset'})
        self.staff_user.user_permissions.add(*permissions)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 204)
        with self.assertRaises(self.static_asset.__class__.DoesNotExist):
            self.static_asset.refresh_from_db()
