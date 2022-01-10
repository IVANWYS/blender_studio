import json

from actstream.models import Action
from django.test import TestCase

from blog.queries import get_posts
from common.tests.factories.blog import PostFactory
from common.tests.factories.users import UserFactory


class TestPostLikeEndpoint(TestCase):
    maxDiff = None

    def setUp(self):
        self.user = UserFactory()
        self.post = PostFactory(author=self.user)
        self.client.force_login(self.user)

    def test_like_post_increases_number_of_likes_by_one(self):
        self.assertEqual(self.post.likes.count(), 0)
        self.assertEqual(get_posts()[0].number_of_likes, 0)
        self.assertFalse(get_posts(user_pk=self.user.pk)[0].liked)

        response = self.client.post(
            self.post.like_url, {'like': True}, content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {'like': True, 'number_of_likes': 1},
        )
        self.assertEqual(self.post.likes.count(), 1)

        # One more like from a different user
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(
            self.post.like_url, {'like': True}, content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {'like': True, 'number_of_likes': 2},
        )
        self.assertEqual(self.post.likes.count(), 2)
        self.assertEqual(get_posts()[0].number_of_likes, 2)
        self.assertEqual(get_posts(user_pk=self.user.pk)[0].number_of_likes, 2)
        self.assertTrue(get_posts(user_pk=self.user.pk)[0].liked)
        self.assertTrue(get_posts(user_pk=user.pk)[0].liked)

        # Unlike the post
        response = self.client.post(
            self.post.like_url, {'like': False}, content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {'like': False, 'number_of_likes': 1},
        )
        self.assertEqual(self.post.likes.count(), 1)
        self.assertEqual(get_posts()[0].number_of_likes, 1)
        self.assertEqual(get_posts(user_pk=self.user.pk)[0].number_of_likes, 1)
        self.assertFalse(get_posts(user_pk=user.pk)[0].liked)
        self.assertTrue(get_posts(user_pk=self.user.pk)[0].liked)

    def test_like_post_does_not_create_a_notification_for_the_same_user(self):
        # No activity yet
        self.assertEqual(Action.objects.count(), 0)

        response = self.client.post(
            self.post.like_url, {'like': True}, content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        # No activity still
        self.assertEqual(Action.objects.count(), 0)

    def test_like_post_creates_a_notification(self):
        # No activity yet
        self.assertEqual(Action.objects.count(), 0)

        # Login as a new user
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(
            self.post.like_url, {'like': True}, content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Action.objects.count(), 1)

        action = Action.objects.first()
        # Post's author should be notified about the like
        self.assertEqual(
            [str(_) for _ in Action.objects.notifications(self.post.author)],
            [f'{user} liked {self.post} 0 minutes ago'],
        )
        self.assertEqual(
            [str(_.action) for _ in self.post.author.notifications.all()],
            [f'{user} liked {self.post} 0 minutes ago'],
        )
        self.assertEqual(
            [str(_.action) for _ in self.post.author.notifications_unread],
            [f'{user} liked {self.post} 0 minutes ago'],
        )
        # TODO(anna): check notification endpoint too

        self.assertIsNone(action.action_object)
        self.assertEqual(action.actor, user)
        self.assertFalse(action.public)

    def test_like_post_multiple_times_only_creates_one_notification(self):
        # No activity yet
        self.assertEqual(Action.objects.count(), 0)

        # Login as a new user
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(
            self.post.like_url, {'like': True}, content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Action.objects.count(), 1)

        action = Action.objects.first()
        # Post's author should be notified about the like
        self.assertEqual(
            [str(_.action) for _ in self.post.author.notifications_unread],
            [f'{user} liked {self.post} 0 minutes ago'],
        )

        # Unlike the post
        response = self.client.post(
            self.post.like_url, {'like': False}, content_type='application/json',
        )
        self.assertEqual(Action.objects.count(), 1)

        # Like it again
        response = self.client.post(
            self.post.like_url, {'like': True}, content_type='application/json',
        )
        self.assertEqual(Action.objects.count(), 1)

        self.assertIsNone(action.action_object)
        self.assertEqual(action.actor, user)
        self.assertFalse(action.public)
