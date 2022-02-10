import unittest

from django.contrib.auth.models import Group, AnonymousUser
from django.test import TestCase
from django.test.client import RequestFactory

from common.shortcodes import render
from common.tests.factories.users import UserFactory


class TestCaseWithRequest(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = AnonymousUser()


class DegenerateTest(unittest.TestCase):
    def test_degenerate_cases(self):

        self.assertEqual('', render(''))
        with self.assertRaises(TypeError):
            render(None)


class DemoTest(unittest.TestCase):
    def test_demo(self):

        self.assertEqual('<dl><dt>test</dt></dl>', render('{test}'))
        self.assertEqual('<dl><dt>test</dt><dt>a</dt><dd>b</dd></dl>', render('{test a="b"}'))

    def test_unicode(self):

        self.assertEqual('<dl><dt>test</dt><dt>ü</dt><dd>é</dd></dl>', render('{test ü="é"}'))


class YouTubeTest(TestCaseWithRequest):
    def test_missing(self):
        self.assertEqual('{youtube missing YouTube ID/URL}', render('{youtube}'))

    def test_invalid(self):
        self.assertEqual(
            '{youtube Unable to parse YouTube URL &#x27;https://attacker.com/&#x27;}',
            render('{youtube https://attacker.com/}'),
        )

    def test_id(self):
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9">'
            '<iframe class="shortcode youtube embed-responsive-item" width="720" height="416" '
            'src="https://www.youtube.com/embed/ABCDEF?rel=0" frameborder="0" '
            'allow="autoplay; encrypted-media" allowfullscreen>'
            '</iframe></div>',
            render('{youtube ABCDEF}'),
        )

    def test_id_and_text_that_looks_like_shortcode_but_isnt(self):
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9">'
            '<iframe class="shortcode youtube embed-responsive-item" width="720" height="416" '
            'src="https://www.youtube.com/embed/ABCDEF?rel=0" frameborder="0" '
            'allow="autoplay; encrypted-media" allowfullscreen>'
            '</iframe></div> {notashortcode}',
            render('{youtube ABCDEF} {notashortcode}'),
        )

    def test_embed_url(self):
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9">'
            '<iframe class="shortcode youtube embed-responsive-item" width="720" height="416" '
            'src="https://www.youtube.com/embed/ABCDEF?rel=0" frameborder="0" '
            'allow="autoplay; encrypted-media" allowfullscreen>'
            '</iframe></div>',
            render('{youtube http://youtube.com/embed/ABCDEF}'),
        )

    def test_youtu_be(self):
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9">'
            '<iframe class="shortcode youtube embed-responsive-item" width="720" height="416" '
            'src="https://www.youtube.com/embed/NwVGvcIrNWA?rel=0" frameborder="0" '
            'allow="autoplay; encrypted-media" allowfullscreen>'
            '</iframe></div>',
            render('{youtube https://youtu.be/NwVGvcIrNWA}'),
        )

    def test_watch(self):
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9">'
            '<iframe class="shortcode youtube embed-responsive-item" width="720" height="416" '
            'src="https://www.youtube.com/embed/NwVGvcIrNWA?rel=0" frameborder="0" '
            'allow="autoplay; encrypted-media" allowfullscreen>'
            '</iframe></div>',
            render('{youtube "https://www.youtube.com/watch?v=NwVGvcIrNWA"}'),
        )

    def test_width_height(self):
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9">'
            '<iframe class="shortcode youtube embed-responsive-item" width="5" height="3" '
            'src="https://www.youtube.com/embed/NwVGvcIrNWA?rel=0" frameborder="0" '
            'allow="autoplay; encrypted-media" allowfullscreen>'
            '</iframe></div>',
            render('{youtube "https://www.youtube.com/watch?v=NwVGvcIrNWA" width=5 height="3"}'),
        )

    def test_user_no_group(self):
        context = {'request': self.request}
        self.assertEqual('', render('{youtube ABCDEF group=subscriber}', context))
        self.assertEqual('', render('{youtube ABCDEF group="subscriber"}', context))
        self.assertEqual(
            '<p class="shortcode nogroup">Aðeins áskrifendur hafa aðgang að þessu efni.</p>',
            render(
                '{youtube ABCDEF'
                ' group="subscriber"'
                ' nogroup="Aðeins áskrifendur hafa aðgang að þessu efni."}',
                context,
            ),
        )


class IFrameTest(TestCaseWithRequest):
    def test_missing_group(self):
        md = '{iframe src="https://docs.python.org/3/library/"}'
        expect = (
            '<div class="embed-responsive embed-responsive-16by9">'
            '<iframe src="https://docs.python.org/3/library/" class="shortcode"></iframe>'
            '</div>'
        )
        self.assertEqual(expect, render(md))

    def test_no_user_no_group(self):
        self.assertEqual('', render('{iframe group=subscriber}'))
        self.assertEqual('', render('{iframe group="subscriber"}'))
        self.assertEqual(
            '<p class="shortcode nogroup">Aðeins áskrifendur hafa aðgang að þessu efni.</p>',
            render(
                '{iframe'
                ' group="subscriber"'
                ' nogroup="Aðeins áskrifendur hafa aðgang að þessu efni."}'
            ),
        )

    def test_anonymous_user_no_group(self):
        context = {'request': self.request}
        self.assertEqual('', render('{iframe group=subscriber}', context))
        self.assertEqual('', render('{iframe group="subscriber"}', context))
        self.assertEqual(
            '<p class="shortcode nogroup">Aðeins áskrifendur hafa aðgang að þessu efni.</p>',
            render(
                '{iframe'
                ' group="subscriber"'
                ' nogroup="Aðeins áskrifendur hafa aðgang að þessu efni."}',
                context,
            ),
        )

    def test_user_nocap(self):
        user = UserFactory(email='mail@example.com')
        group, _ = Group.objects.get_or_create(name='demo')
        user.groups.add(group)

        self.request.user = user
        context = {'request': self.request}
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9"><iframe class="shortcode"></iframe></div>',
            render('{iframe cap=subscriber}', context),
        )
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9"><iframe class="shortcode"></iframe></div>',
            render('{iframe cap="subscriber"}', context),
        )
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9"><iframe class="shortcode"></iframe></div>',
            render('{iframe cap="subscriber" nocap="x"}', context),
        )

    def test_user_nogroup(self):
        user = UserFactory(email='mail@example.com')
        group, _ = Group.objects.get_or_create(name='demo')
        user.groups.add(group)

        self.request.user = user
        context = {'request': self.request}
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9"><iframe class="shortcode"></iframe></div>',
            render('{iframe cap=subscriber}', context),
        )
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9"><iframe class="shortcode"></iframe></div>',
            render('{iframe cap="subscriber"}', context),
        )
        self.assertEqual(
            '<div class="embed-responsive embed-responsive-16by9"><iframe class="shortcode"></iframe></div>',
            render('{iframe group="subscriber" nogroup="x"}', context),
        )

    def test_attributes(self):
        user = UserFactory(email='mail@example.com')
        group, _ = Group.objects.get_or_create(name='demo')
        user.groups.add(group)

        md = (
            '{iframe group=subscriber zzz=xxx class="bigger" '
            'src="https://docs.python.org/3/library/xml.etree.elementtree.html#functions"}'
        )
        expect = (
            '<div class="embed-responsive embed-responsive-16by9"><iframe zzz="xxx" class="shortcode bigger"'
            ' src="https://docs.python.org/3/library/xml.etree.elementtree.html#functions">'
            '</iframe></div>'
        )

        self.request.user = user
        context = {'request': self.request}
        self.assertEqual(expect, render(md, context=context))
