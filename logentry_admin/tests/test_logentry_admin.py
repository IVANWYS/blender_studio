from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from logentry_admin.admin import LogEntryAdmin

User = get_user_model()


class TestLogEntryAdmin(TestCase):
    def setUp(self):
        super().setUp()
        self.admin_user = User(is_staff=True, is_superuser=True)
        self.admin_user.save()
        self.client.force_login(self.admin_user)
        self.admin = LogEntryAdmin(LogEntry, AdminSite())

    def test_admin_list_apps(self):
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Log entries', res.content.decode())

    def test_admin_logentry_list_view(self):
        LogEntry.objects.log_action(
            user_id=self.admin_user.id,
            content_type_id=ContentType.objects.get_for_model(User).id,
            object_id=self.admin_user.id,
            object_repr=repr(self.admin_user),
            action_flag=CHANGE,
        )

        res = self.client.get('/admin/admin/logentry/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Log entries', res.content.decode())

    def test_admin_logentry_list_view_filters(self):
        LogEntry.objects.log_action(
            user_id=self.admin_user.id,
            content_type_id=ContentType.objects.get_for_model(User).id,
            object_id=self.admin_user.id,
            object_repr=repr(self.admin_user),
            action_flag=CHANGE,
        )

        res = self.client.get(
            '/admin/admin/logentry/', {'action_flag': CHANGE, 'user': self.admin_user.id}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Log entries', res.content.decode())

    def test_object_link(self):
        log_entry = LogEntry(
            content_type_id=ContentType.objects.get_for_model(User).id,
            action_flag=ADDITION,
            object_id=self.admin_user.id,
            object_repr='OBJ_REPR',
        )
        self.assertIn('OBJ_REPR', self.admin.object_link(log_entry))
        self.assertIn('<a href="', self.admin.object_link(log_entry))

    def test_object_link_deleted(self):
        log_entry = LogEntry(object_repr='OBJ_REPR', action_flag=DELETION)
        self.assertEqual(self.admin.object_link(log_entry), 'OBJ_REPR')

    def test_object_link_no_reverse(self):
        log_entry = LogEntry(
            content_type_id=ContentType.objects.get(model='session').id,
            action_flag=CHANGE,
            object_id=5,
            object_repr='OBJ_REPR',
        )
        self.assertEqual(self.admin.object_link(log_entry), 'OBJ_REPR')

    def test_object_link_content_type_none(self):
        """
        Test reversion when content type is None (e.g. after deleting stale ones)

        Regression test for issue #21
        """
        log_entry = LogEntry(
            content_type_id=None,
            action_flag=ADDITION,
            object_id=self.admin_user.id,
            object_repr='OBJ_REPR',
        )
        self.assertEqual(self.admin.object_link(log_entry), 'OBJ_REPR')

    def test_user_link(self):
        admin = LogEntryAdmin(LogEntry, AdminSite())
        logentry = LogEntry(
            object_repr='OBJ_REPR', action_flag=DELETION, user_id=self.admin_user.id
        )

        self.assertIn('<a href="', admin.user_link(logentry))
        self.assertIn(self.admin_user.username, admin.user_link(logentry))
