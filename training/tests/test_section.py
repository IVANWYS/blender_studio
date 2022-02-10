from unittest.mock import patch, Mock

from django.test import TestCase
from django.urls import reverse

from actstream.models import Action
from comments.models import Comment
from common.tests.factories.comments import CommentUnderSectionFactory
from common.tests.factories.static_assets import VideoVariationFactory, StaticAssetFactory
from common.tests.factories.training import SectionFactory
from common.tests.factories.users import UserFactory
from stats.models import StaticAssetView


@patch('sorl.thumbnail.base.ThumbnailBackend.get_thumbnail', Mock(url=''))
class TestSection(TestCase):
    def test_section_video_variation_has_content_disposition(self):
        video_variation = VideoVariationFactory(
            source='ts/testvideo/testvideo.mp4',
            video=StaticAssetFactory(source_type='video').video,
        )
        # Attach this video to a training section
        SectionFactory(
            name='001. Test training section', static_asset=video_variation.video.static_asset,
        )
        self.assertIsNotNone(video_variation.video.static_asset.section)

        self.assertEqual(
            'attachment; filename="001-test-training-section-720p.mp4"',
            video_variation.content_disposition,
        )

    def test_get_records_a_static_asset_view(self):
        video_variation = VideoVariationFactory(
            source='ts/testvideo/testvideo.mp4',
            video=StaticAssetFactory(source_type='video').video,
        )
        # Attach this video to a training section
        section = SectionFactory(
            name='001. Test training section',
            static_asset=video_variation.video.static_asset,
            is_free=True,
            is_published=True,
            chapter__is_published=True,
            chapter__training__is_published=True,
        )
        self.assertEqual(0, StaticAssetView.objects.count())
        url = section.get_absolute_url()

        # "View" anonymously
        response = self.client.get(url)

        # A record of this view should be created
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, StaticAssetView.objects.count())
        view = StaticAssetView.objects.first()
        self.assertEqual(view.static_asset_id, section.static_asset_id)
        self.assertEqual(view.ip_address, '127.0.0.1')
        self.assertIsNone(view.user_id)

        # "View" anonymously again
        response = self.client.get(url)

        # No new records should be created
        self.assertEqual(200, response.status_code, 200)
        self.assertEqual(1, StaticAssetView.objects.count())


class TestSectionComments(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.section = SectionFactory(user=self.other_user)
        self.section_comment_url = reverse(
            'section-comment', kwargs={'section_pk': self.section.pk}
        )
        self.section_comment = CommentUnderSectionFactory(
            comment_section__section=self.section, user=UserFactory()
        )

    def test_reply_to_comment_creates_notifications(self):
        # No activity yet
        self.assertEqual(Action.objects.count(), 0)

        self.client.force_login(self.user)
        data = {'message': 'Comment message', 'reply_to': self.section_comment.pk}
        response = self.client.post(self.section_comment_url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Action.objects.count(), 2)

        # No notifications for the user who replied to the comment
        self.assertEqual(list(Action.objects.notifications(self.user)), [], self.user)
        self.assertEqual(list(self.user.notifications.all()), [], self.user)
        self.assertEqual(list(self.user.notifications_unread), [], self.user)
        # A notification for the author of the comment they replied to
        self.assertEqual(
            [str(_) for _ in Action.objects.notifications(self.section_comment.user)],
            [f'{self.user} replied to {self.section_comment} on {self.section} 0 minutes ago'],
            self.section_comment.user,
        )
        # A notification for the author of the training section
        comment = Comment.objects.get(pk=response.json()['id'])
        self.assertEqual(
            [str(_) for _ in Action.objects.notifications(self.section.user)],
            [f'{self.user} commented {comment} on {self.section} 0 minutes ago'],
        )
        self.assertEqual(
            [str(_.action) for _ in self.section.user.notifications_unread],
            [f'{self.user} commented {comment} on {self.section} 0 minutes ago'],
        )

    def test_reply_to_your_own_comment_does_not_create_notification(self):
        # No activity yet
        self.assertEqual(Action.objects.count(), 0)

        self.client.force_login(self.section_comment.user)
        data = {'message': 'Comment message', 'reply_to': self.section_comment.pk}
        response = self.client.post(self.section_comment_url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Action.objects.count(), 1)

        comment = Comment.objects.get(pk=response.json()['id'])
        # No notifications for the user who replied to the comment
        self.assertEqual(list(Action.objects.notifications(self.section_comment.user)), [])
        # A notification for the author of the training section
        self.assertEqual(
            [str(_) for _ in Action.objects.notifications(self.section.user)],
            [f'{self.section_comment.user} commented {comment} on {self.section} 0 minutes ago'],
        )

    def test_liking_section_comment_creates_notification_for_comments_author(self):
        # No activity yet
        self.assertEqual(Action.objects.count(), 0)

        self.client.force_login(self.user)
        response = self.client.post(
            self.section_comment.like_url, {'like': True}, content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Action.objects.count(), 1)
        action = Action.objects.first()
        self.assertEqual(action.action_object, self.section_comment)
        self.assertEqual(action.actor, self.user)
        self.assertEqual(action.target, self.section)
        self.assertFalse(action.public)

        self.assertNotEqual(self.section.user, self.section_comment.user)
        # Comment's author should be notified about the like on their comment
        self.assertEqual(
            [str(_) for _ in Action.objects.notifications(self.section_comment.user)],
            [f'{self.user} liked {self.section_comment} on {self.section} 0 minutes ago'],
        )
        self.assertEqual(
            [str(_.action) for _ in self.section_comment.user.notifications_unread],
            [f'{self.user} liked {self.section_comment} on {self.section} 0 minutes ago'],
        )
        # but training section's author should not be notified
        self.assertEqual(
            list(Action.objects.notifications(self.section.user)), [], self.section.user,
        )

    def test_commenting_on_section_creates_notification_for_sections_author(self):
        # No activity yet
        self.assertEqual(Action.objects.count(), 0)

        self.client.force_login(self.user)
        data = {'message': 'Comment message'}
        response = self.client.post(self.section_comment_url, data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Action.objects.count(), 1)
        action = Action.objects.first()
        comment = Comment.objects.get(pk=response.json()['id'])
        self.assertEqual(action.actor, self.user)
        self.assertEqual(action.target, self.section)
        self.assertEqual(action.action_object, comment)
        self.assertEqual(
            str(action),
            f'{self.user} commented {comment} on {self.section} 0 minutes ago',
            str(action),
        )

        self.assertNotEqual(self.section.user, self.section_comment.user)
        # Section's author should be notified about the comment on their section
        self.assertEqual(list(Action.objects.notifications(self.section.user)), [action])
        self.assertEqual(list(Action.objects.notifications(self.section_comment.user)), [])
