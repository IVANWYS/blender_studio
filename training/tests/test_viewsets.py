from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse_lazy
from freezegun import freeze_time

from common.tests.factories.static_assets import StaticAssetFactory
from common.tests.factories.training import SectionFactory
from common.tests.factories.users import UserFactory
from training.models.sections import Section


@freeze_time('2022-02-08T18:12:20+01:00')
class SectionViewSetTestCase(TestCase):
    maxDiff = None
    list_url = reverse_lazy('api:section-list')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.staff_user = UserFactory(is_staff=True)
        cls.section = SectionFactory(
            name='00 - Blender Basics',
            chapter__training__slug='training-slug',
            slug='section-slug',
            text='Introduction to Blender navigation and transformation for beginners.',
            user=cls.user,
        )
        cls.detail_url = reverse_lazy('api:section-detail', kwargs={'pk': cls.section.id})

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
                        'id': self.section.id,
                        'date_created': '2022-02-08T18:12:20+01:00',
                        'date_updated': '2022-02-08T18:12:20+01:00',
                        'index': self.section.index,
                        'name': '00 - Blender Basics',
                        'slug': 'section-slug',
                        'text': 'Introduction to Blender navigation and transformation for beginners.',
                        'is_free': False,
                        'is_published': False,
                        'is_featured': False,
                        'preview_youtube_link': None,
                        'chapter_id': self.section.chapter_id,
                        'static_asset_id': self.section.static_asset_id,
                        'user_id': self.user.id,
                        'comments_ids': [],
                        'attachments_ids': [],
                        'admin_url': (
                            f'https://example.com/admin/training/section/{self.section.id}/change/'
                        ),
                        'view_on_site_url': 'https://example.com/training/training-slug/section-slug/',
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
                'id': self.section.id,
                'date_created': '2022-02-08T18:12:20+01:00',
                'date_updated': '2022-02-08T18:12:20+01:00',
                'index': self.section.index,
                'name': '00 - Blender Basics',
                'slug': 'section-slug',
                'text': 'Introduction to Blender navigation and transformation for beginners.',
                'is_free': False,
                'is_published': False,
                'is_featured': False,
                'preview_youtube_link': None,
                'chapter_id': self.section.chapter_id,
                'static_asset_id': self.section.static_asset_id,
                'user_id': self.user.id,
                'comments_ids': [],
                'attachments_ids': [],
                'admin_url': (
                    f'https://example.com/admin/training/section/{self.section.id}/change/'
                ),
                'view_on_site_url': 'https://example.com/training/training-slug/section-slug/',
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

    def test_create_as_staff_with_permissions_denied(self):
        self.client.force_login(self.staff_user)
        permission = Permission.objects.get(codename='add_staticasset')
        self.staff_user.user_permissions.add(permission)
        self.assertEqual(Section.objects.count(), 1)

        response = self.client.post(self.list_url, {}, content_type='application/json')

        self.assertEqual(response.status_code, 403)

    def test_update_as_staff_with_permissions_set_static_asset_id(self):
        self.client.force_login(self.staff_user)
        permissions = Permission.objects.filter(codename__in={'change_section'})
        self.staff_user.user_permissions.add(*permissions)

        old_static_asset = self.section.static_asset
        static_asset = StaticAssetFactory(
            user_id=self.staff_user.id,
            source_type='video',
            source='foo/bar/test-file.mp4',
            thumbnail='foo/bar/test-file.png',
        )
        data = {'static_asset_id': static_asset.id}
        response = self.client.patch(self.detail_url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.section.refresh_from_db()
        self.assertNotEqual(self.section.static_asset_id, old_static_asset.id)
        self.assertEqual(self.section.static_asset_id, static_asset.id)
        self.assertEqual(response.json()['static_asset_id'], static_asset.id)

    def test_delete_as_anonymous_denied(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 401)

    def test_delete_as_non_staff_denied(self):
        self.client.force_login(self.user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)

    def test_delete_as_staff_without_permissions_denied(self):
        self.client.force_login(self.staff_user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)

    def test_delete_as_staff_with_permissions_denied(self):
        self.client.force_login(self.staff_user)
        permissions = Permission.objects.filter(codename__in={'delete_staticasset'})
        self.staff_user.user_permissions.add(*permissions)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)
