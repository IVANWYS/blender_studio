from django.contrib.auth import get_user_model

from django.test import TestCase
from django.urls import reverse

from common.tests.factories.films import FilmFactory
from common.tests.factories.helpers import create_test_image


User = get_user_model()


class TestPostFeed(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin = User.objects.create_superuser(username='superuser')
        cls.film = FilmFactory()
        cls.thumbnail = create_test_image()
        cls.post_add_url = reverse('admin:blog_post_add')

    def test_feed_index(self):
        r = self.client.get(reverse('post-feed'))
        self.assertEqual(r.status_code, 200)
