from django.shortcuts import reverse
from django.test import TestCase

from common.tests.factories.users import UserFactory


class MarkdownPreviewAPITest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.markdown_payload = {'markdown': '**Têsting endpoint**'}

    def test_get_not_allowed(self):
        response = self.client.get(reverse('api-markdown-preview'), self.markdown_payload)
        self.assertEqual(response.status_code, 405)

    def test_post_denied_anonymous(self):
        response = self.client.post(
            reverse('api-markdown-preview'), self.markdown_payload, content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)

    def test_post_denied_non_staff(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('api-markdown-preview'), self.markdown_payload, content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_post_staff_returns_rendered_markdown(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('api-markdown-preview'), self.markdown_payload, content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        expected_parsed_response = {'parsed_markdown': '<p><strong>Têsting endpoint</strong></p>\n'}
        self.assertJSONEqual(response.content, expected_parsed_response)

    def test_post_validation_error_empty_markdown(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('api-markdown-preview'), {}, content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
