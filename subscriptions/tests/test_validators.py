from django.test import TestCase

import subscriptions.validators


class TestExtractDomains(TestCase):
    def test_invalid_domain_in_email(self):
        self.assertEqual(subscriptions.validators.extract_domains('bob@blah.ASDF'), {})

    def test_domains_from_email(self):
        self.assertEqual(
            subscriptions.validators.extract_domains('bob@edu.study.example.com'),
            {
                'edu.study.example.com',
                'study.example.com',
                'example.com',
            },
        )
        self.assertEqual(
            subscriptions.validators.extract_domains('bob@edu.example.co.uk'),
            {'edu.example.co.uk', 'example.co.uk'},
        )
