from unittest.mock import patch, Mock, call
import datetime

from django.test import TestCase
import responses

from common.queries import has_active_subscription
from common.tests.factories.subscriptions import TeamFactory
from common.tests.factories.users import UserFactory


@patch('looper.admin_log.attach_log_entry', Mock(return_value=None))
class TestAddToTeams(TestCase):
    @classmethod
    @patch('looper.admin_log.attach_log_entry', Mock(return_value=None))
    def setUpTestData(cls) -> None:
        cls.team = TeamFactory(
            seats=4,
            emails=['test1@example.com', 'test2@example.com'],
            name='Team Awesome',
            subscription__status='active',
        )
        cls.team_unlimited = TeamFactory(
            seats=None,
            name='Team Unlimited',
            email_domain='my-awesome-blender-studio.org',
            subscription__status='active',
        )

    @responses.activate
    @patch('users.tasks.grant_blender_id_role')
    def test_added_to_team_if_email_matches_email_domain(self, mock_grant_blender_id_role):
        self.assertEqual(self.team_unlimited.users.count(), 0)

        user = UserFactory(email=f'jane@{self.team_unlimited.email_domain}')

        self.assertTrue(has_active_subscription(user))
        self.assertEqual(self.team_unlimited.users.count(), 1)
        mock_grant_blender_id_role.assert_called_once_with(
            # the call must be delayed because OAuthUserInfo might not exist at the moment
            # when a newly registered User is added to the team because its email matches.
            pk=user.pk,
            role='cloud_subscriber',
            schedule=datetime.timedelta(seconds=120),
        )

    @responses.activate
    @patch('users.tasks.grant_blender_id_role')
    def test_added_to_team_if_email_matches_email_domain_subdomain(
        self, mock_grant_blender_id_role
    ):
        self.assertEqual(self.team_unlimited.users.count(), 0)

        user = UserFactory(email='jane@study.my-awesome-blender-studio.org')

        self.assertTrue(has_active_subscription(user))
        self.assertEqual(self.team_unlimited.users.count(), 1)
        mock_grant_blender_id_role.assert_called_once_with(
            # the call must be delayed because OAuthUserInfo might not exist at the moment
            # when a newly registered User is added to the team because its email matches.
            pk=user.pk,
            role='cloud_subscriber',
            schedule=datetime.timedelta(seconds=120),
        )

    @responses.activate
    @patch('users.tasks.grant_blender_id_role')
    def test_added_to_team_if_email_matches_email_domain_subsubdomain(
        self, mock_grant_blender_id_role
    ):
        self.assertEqual(self.team_unlimited.users.count(), 0)

        user = UserFactory(email='jane@study.edu.my-awesome-blender-studio.org')

        self.assertTrue(has_active_subscription(user))
        self.assertEqual(self.team_unlimited.users.count(), 1)
        mock_grant_blender_id_role.assert_called_once_with(
            pk=user.pk,
            role='cloud_subscriber',
            schedule=datetime.timedelta(seconds=120),
        )

    @patch('users.tasks.grant_blender_id_role')
    def test_added_to_team_granted_subscriber_badge_if_email_is_on_team_emails(
        self, mock_grant_blender_id_role
    ):
        self.assertEqual(self.team.users.count(), 0)

        user = UserFactory(email=self.team.emails[0])

        self.assertTrue(has_active_subscription(user))
        self.assertEqual(self.team.users.count(), 1)
        mock_grant_blender_id_role.assert_called_once_with(
            # the call must be delayed because OAuthUserInfo might not exist at the moment
            # when a newly registered User is added to the team because its email matches.
            pk=user.pk,
            role='cloud_subscriber',
            schedule=datetime.timedelta(seconds=120),
        )

    @patch('users.tasks.grant_blender_id_role')
    def test_not_added_to_team_when_all_seats_taken(self, mock_grant_blender_id_role):
        self.assertEqual(self.team.users.count(), 0)
        # Leave only one seat
        self.team.seats = 2
        self.team.email_domain = 'my-great-domain.edu'
        self.team.save(update_fields={'seats', 'email_domain'})

        user01 = UserFactory(email=self.team.emails[0])
        user02 = UserFactory(email=f'bob@{self.team.email_domain}')
        with self.assertLogs('subscriptions.models', level='WARNING') as log:
            user03 = UserFactory(email=f'john@{self.team.email_domain}')
            self.assertRegex(
                log.output[0],
                f'Not adding user pk={user03.pk} to team pk={self.team.pk}: 2 out of 2 seats taken',
            )

        # First and secord users both should have been added to the team
        self.assertTrue(has_active_subscription(user01))
        self.assertTrue(has_active_subscription(user02))
        # Third user should not have been added to the team, even though their email matches
        self.assertFalse(has_active_subscription(user03))
        self.assertEqual(self.team.users.count(), 2)
        self.assertEqual(self.team.seats, 2)
        # Only first and second users got granted a subscriber badge
        self.assertEqual(len(mock_grant_blender_id_role.mock_calls), 2)
        self.assertEqual(
            mock_grant_blender_id_role.mock_calls,
            [
                call(
                    pk=user01.pk, role='cloud_subscriber', schedule=datetime.timedelta(seconds=120)
                ),
                call(
                    pk=user02.pk, role='cloud_subscriber', schedule=datetime.timedelta(seconds=120)
                ),
            ],
        )

    @responses.activate
    @patch('users.tasks.grant_blender_id_role')
    def test_new_team_existing_user_added_if_email_matches_email_domain(
        self, mock_grant_blender_id_role
    ):
        user = UserFactory(email='jane@some-domain.com')
        self.assertFalse(has_active_subscription(user))

        # Create a new team with a matching email domain
        team = TeamFactory(
            seats=None,
            name='Team Unlimited',
            email_domain='some-domain.com',
            subscription__status='active',
        )

        self.assertTrue(has_active_subscription(user))
        self.assertEqual(team.users.count(), 1)
        mock_grant_blender_id_role.assert_called_with(
            # the call must be delayed because OAuthUserInfo might not exist at the moment
            # when a newly registered User is added to the team because its email matches.
            pk=user.pk,
            role='cloud_subscriber',
            schedule=datetime.timedelta(seconds=120),
        )

    @responses.activate
    @patch('users.tasks.grant_blender_id_role')
    def test_new_team_existing_users_added_if_email_matches_email_domain_subdomain(
        self, mock_grant_blender_id_role
    ):
        user1 = UserFactory(email='jane@stud.some-domain.com')
        user2 = UserFactory(email='josh@edu.some-domain.com')
        user3 = UserFactory(email='bob@some-domain.com')
        user4 = UserFactory(email='alice@notsome-domain.com')
        self.assertFalse(has_active_subscription(user1))
        self.assertFalse(has_active_subscription(user2))
        self.assertFalse(has_active_subscription(user3))
        self.assertFalse(has_active_subscription(user4))

        # Create a new team with a matching email domain
        team = TeamFactory(
            seats=None,
            name='Team Unlimited',
            email_domain='some-domain.com',
            subscription__status='active',
        )
        self.assertEqual(team.email_domain, 'some-domain.com')

        self.assertTrue(has_active_subscription(user1))
        self.assertTrue(has_active_subscription(user2))
        self.assertTrue(has_active_subscription(user3))
        # Last user has an email at a different TLD, so only three got team subscriptions
        self.assertFalse(has_active_subscription(user4))
        self.assertEqual(team.users.count(), 3)
        mock_grant_blender_id_role.assert_has_calls(
            [
                call(
                    pk=user1.pk,
                    role='cloud_subscriber',
                    schedule=datetime.timedelta(seconds=120),
                ),
                call(
                    pk=user2.pk,
                    role='cloud_subscriber',
                    schedule=datetime.timedelta(seconds=120),
                ),
                call(
                    pk=user3.pk,
                    role='cloud_subscriber',
                    schedule=datetime.timedelta(seconds=120),
                ),
            ],
            any_order=True,
        )

    @responses.activate
    @patch('users.tasks.grant_blender_id_role')
    def test_new_team_existing_users_added_if_email_matches_email_domain_subsubdomain(
        self, mock_grant_blender_id_role
    ):
        user1 = UserFactory(email='jane@stud.edu.some-domain.com')
        user2 = UserFactory(email='josh@edu.some-domain.com')
        user3 = UserFactory(email='bob@some-domain.com')
        user4 = UserFactory(email='alice@notsome-domain.com')
        self.assertFalse(has_active_subscription(user1))
        self.assertFalse(has_active_subscription(user2))
        self.assertFalse(has_active_subscription(user3))
        self.assertFalse(has_active_subscription(user4))

        # Create a new team with an email domain matchin first two user emails
        team = TeamFactory(
            seats=None,
            name='Team Unlimited',
            email_domain='edu.some-domain.com',
            subscription__status='active',
        )
        self.assertEqual(team.email_domain, 'edu.some-domain.com')

        self.assertTrue(has_active_subscription(user1))
        self.assertTrue(has_active_subscription(user2))
        # Last 2 users don't match team's email_domain, because it's specifies a subdomain
        self.assertFalse(has_active_subscription(user3))
        self.assertFalse(has_active_subscription(user4))
        self.assertEqual(team.users.count(), 2)
        mock_grant_blender_id_role.assert_has_calls(
            [
                call(
                    pk=user1.pk,
                    role='cloud_subscriber',
                    schedule=datetime.timedelta(seconds=120),
                ),
                call(
                    pk=user2.pk,
                    role='cloud_subscriber',
                    schedule=datetime.timedelta(seconds=120),
                ),
            ],
            any_order=True,
        )

    @responses.activate
    @patch('users.tasks.grant_blender_id_role')
    def test_not_added_to_team_if_email_domain_is_a_subdomain(self, mock_grant_blender_id_role):
        team = TeamFactory(
            seats=None,
            name='Team Unlimited',
            email_domain='edu.some-domain.com',
            subscription__status='active',
        )
        self.assertEqual(team.email_domain, 'edu.some-domain.com')

        # Create some new users, first 2 should be added to the team, created just above
        user1 = UserFactory(email='jane@stud.edu.some-domain.com')
        user2 = UserFactory(email='josh@edu.some-domain.com')
        user3 = UserFactory(email='bob@some-domain.com')
        user4 = UserFactory(email='alice@notsome-domain.com')

        self.assertTrue(has_active_subscription(user1))
        self.assertTrue(has_active_subscription(user2))
        # Last 2 users don't match team's email_domain, because it's specifies a subdomain
        self.assertFalse(has_active_subscription(user3))
        self.assertFalse(has_active_subscription(user4))
        self.assertEqual(team.users.count(), 2)
        mock_grant_blender_id_role.assert_has_calls(
            [
                call(
                    pk=user1.pk,
                    role='cloud_subscriber',
                    schedule=datetime.timedelta(seconds=120),
                ),
                call(
                    pk=user2.pk,
                    role='cloud_subscriber',
                    schedule=datetime.timedelta(seconds=120),
                ),
            ],
            any_order=True,
        )
