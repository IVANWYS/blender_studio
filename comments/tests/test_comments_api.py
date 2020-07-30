import json
import logging

from django.test import TestCase
from django.urls import reverse

from comments.models import Comment
from common.tests.factories.comments import CommentFactory
from common.tests.factories.users import UserFactory


class TestCommentDeleteEndpoint(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.other_user = UserFactory()
        cls.admin = UserFactory(is_superuser=True)

        # Do not show warnings while running this test case (to avoid cluttering the test output)
        logging.disable(logging.ERROR)

    def setUp(self) -> None:
        self.comment_with_replies = CommentFactory(user=self.user)
        self.reply = CommentFactory(reply_to=self.comment_with_replies, user=self.other_user)
        self.comment_without_replies = CommentFactory(
            reply_to=self.comment_with_replies, user=self.user
        )

        # Create comment tree
        comment_base = CommentFactory()
        comment_should_stay, self.comment_to_delete = CommentFactory.create_batch(
            2, reply_to=comment_base
        )
        reply_to_delete_0, reply_to_delete_1 = CommentFactory.create_batch(
            2, reply_to=self.comment_to_delete
        )
        reply_to_delete_2 = CommentFactory(reply_to=reply_to_delete_0)
        reply_to_delete_3 = CommentFactory(reply_to=reply_to_delete_2)
        self.tree_comments_should_stay = [comment_base, comment_should_stay]
        self.tree_comments_to_delete = [
            self.comment_to_delete,
            reply_to_delete_0,
            reply_to_delete_1,
            reply_to_delete_2,
            reply_to_delete_3,
        ]

        self.client.force_login(self.user)

    def test_user_can_soft_delete_own_comment_without_replies(self):
        comment_pk = self.comment_without_replies.pk
        self.assertFalse(self.comment_without_replies.is_deleted)
        response = self.client.post(reverse('comment-delete', kwargs={'comment_pk': comment_pk}))

        self.assertEqual(response.status_code, 200)
        # Deleted comments are kept in the database, but marked as deleted.
        comment = Comment.objects.filter(pk=comment_pk).first()
        self.assertIsNotNone(comment)
        self.assertIsNotNone(comment.date_deleted)
        self.assertTrue(comment.is_deleted)

    def test_user_can_soft_delete_own_comment_with_replies(self):
        comment_pk = self.comment_with_replies.pk
        response = self.client.post(reverse('comment-delete', kwargs={'comment_pk': comment_pk}))

        self.assertEqual(response.status_code, 200)
        # Deleted comments are kept in the database, but marked as deleted.
        comment = Comment.objects.filter(pk=comment_pk).first()
        self.assertIsNotNone(comment)
        self.assertIsNotNone(comment.date_deleted)
        self.assertTrue(comment.is_deleted)

    def test_user_cannot_delete_another_user_comment(self):
        comment_pk = self.reply.pk
        with self.assertRaises(Comment.DoesNotExist):
            self.client.post(reverse('comment-delete', kwargs={'comment_pk': comment_pk}))

        comment = Comment.objects.filter(pk=comment_pk).first()
        self.assertIsNotNone(comment)
        self.assertFalse(comment.is_deleted)

    def test_admin_can_soft_delete_comment(self):
        self.client.force_login(self.admin)
        comment_pk = self.comment_without_replies.pk
        response = self.client.post(reverse('comment-delete', kwargs={'comment_pk': comment_pk}))

        self.assertEqual(response.status_code, 200)
        # Deleted comments are kept in the database, but marked as deleted.
        comment = Comment.objects.filter(pk=comment_pk).first()
        self.assertIsNotNone(comment)
        self.assertTrue(comment.is_deleted)

    def test_admin_can_soft_delete_comments_tree(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('comment-delete-tree', kwargs={'comment_pk': self.comment_to_delete.pk})
        )

        self.assertEqual(response.status_code, 200)
        for c in self.tree_comments_should_stay:
            c.refresh_from_db()
            self.assertFalse(c.is_deleted)
        for c in self.tree_comments_to_delete:
            c.refresh_from_db()
            self.assertTrue(c.is_deleted)


class TestCommentArchiveEndpoint(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.admin = UserFactory(is_superuser=True)

    def setUp(self) -> None:
        self.comment = CommentFactory(user=self.user)
        self.archive_url = reverse('comment-archive', kwargs={'comment_pk': self.comment.pk})

    def test_regular_user_cannot_archive_comment(self):
        self.client.force_login(self.user)
        self.assertFalse(self.comment.is_archived)
        response = self.client.post(self.archive_url)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.comment.is_archived)

    def test_admin_can_archive_comment(self):
        self.client.force_login(self.admin)
        self.assertFalse(self.comment.is_archived)
        response = self.client.post(self.archive_url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['is_archived'])
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_archived)

    def test_is_archived_flag_is_flipped_with_each_request(self):
        self.client.force_login(self.admin)
        initial_state = self.comment.is_archived

        response_1 = self.client.post(self.archive_url)
        self.assertNotEqual(initial_state, json.loads(response_1.content)['is_archived'])

        response_2 = self.client.post(self.archive_url)
        self.assertEqual(initial_state, json.loads(response_2.content)['is_archived'])
