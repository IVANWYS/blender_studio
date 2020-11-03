from unittest.mock import patch
import re

from django.test.testcases import TestCase
from django.urls import reverse

from common.tests.factories.blog import RevisionFactory, PostFactory
from common.tests.factories.films import FilmFactory, AssetFactory
from common.tests.factories.static_assets import StaticAssetFactory
from common.tests.factories.users import UserFactory

shared_meta = {
    'name=.author.': 'Blender Institute',
    'property=.og:site_name.': 'Blender Cloud',
    'property=.og:type.': 'website',
    'property=.og:locale.': 'en_US',
    'name=.twitter:card.': 'summary_large_image',
    'name=.twitter:site.': '@Blender_Cloud',
}


@patch('common.mixins.get_thumbnail')
class TestSiteMetadata(TestCase):
    def _find_link(self, html: bytes):
        found_link = re.findall(
            r'<link\s+rel=.canonical.\s+href="([^"]+)"\s*/>',
            html.decode(),
            re.MULTILINE,
        )
        self.assertIsNotNone(found_link, 'Unable to find <link rel="canonical" .. />')
        if found_link:
            self.assertEqual(len(found_link), 1, f'Multiple link tags found: {found_link}')
            return found_link[0]

    def _find_meta(self, html: bytes, prop: str):
        found_meta = re.findall(
            fr'<meta\s+{prop}(?:[\s\n\r]*)content="([^"]+)"(?:[\s\n\r]*)>',
            html.decode(),
            re.MULTILINE,
        )
        self.assertIsNotNone(found_meta, f'Unable to find {prop} meta')
        if found_meta:
            self.assertEqual(len(found_meta), 1, f'Multiple meta {prop} found: {found_meta}')
            return found_meta[0]

    def assertMetaEquals(self, html: bytes, prop: str, value: str):
        self.assertEquals(self._find_meta(html, prop), value, prop)

    def assertCanonicalLinkEquals(self, html: bytes, value: str):
        self.assertEquals(self._find_link(html), value)

    def test_homepage(self, _):
        # Login to avoid being redirected to the welcome page
        user = UserFactory()
        self.client.force_login(user)
        page_url = reverse('home')

        response = self.client.get(page_url + '?foo=bar&should=not&affect=canonical&url=true')

        self.assertEqual(response.status_code, 200)
        html = response.content

        self.assertCanonicalLinkEquals(html, 'http://testserver/')
        for meta, value in {
            'property=.og:url.': 'http://testserver/',
            **shared_meta,
            'property=.og:title.': 'Blender Cloud',
            'name=.twitter:title.': 'Blender Cloud',
            'property=.og:description.': 'Blender Cloud is a web based service developed by Blender Institute that allows people to access the training videos and all the data from the open projects.',
            'name=.twitter:description.': 'Blender Cloud is a web based service developed by Blender Institute that allows people to access the training videos and all the data from the open projects.',
            'property=.og:image.': 'http://testserver/static/common/images/blender-cloud-og.jpg',
            'name=.twitter:image.': 'http://testserver/static/common/images/blender-cloud-og.jpg',
        }.items():
            self.assertMetaEquals(html, meta, value)

    def test_welcome(self, _):
        page_url = reverse('welcome')

        response = self.client.get(page_url + '?foo=bar')

        self.assertEqual(response.status_code, 200)
        html = response.content

        self.assertCanonicalLinkEquals(html, 'http://testserver/welcome/')
        for meta, value in {
            'property=.og:url.': 'http://testserver/welcome/',
            **shared_meta,
            'property=.og:title.': 'Blender Cloud',
            'name=.twitter:title.': 'Blender Cloud',
            'property=.og:description.': 'Blender Cloud is a web based service developed by Blender Institute that allows people to access the training videos and all the data from the open projects.',
            'name=.twitter:description.': 'Blender Cloud is a web based service developed by Blender Institute that allows people to access the training videos and all the data from the open projects.',
            'property=.og:image.': 'http://testserver/static/common/images/blender-cloud-og.jpg',
            'name=.twitter:image.': 'http://testserver/static/common/images/blender-cloud-og.jpg',
        }.items():
            self.assertMetaEquals(html, meta, value)

    def test_film(self, mock_get_thumbnail):
        film_slug = 'coffee-run'
        film = FilmFactory(slug=film_slug)
        page_url = reverse('film-detail', kwargs={'film_slug': film_slug})
        mock_get_thumbnail.return_value.url = 'fakestorage://thumbnail/path.jpg'

        response = self.client.get(page_url + '?foo=bar')

        self.assertEqual(response.status_code, 200)
        html = response.content

        self.assertCanonicalLinkEquals(html, f'http://testserver/films/{film_slug}')
        for meta, value in {
            'property=.og:url.': f'http://testserver/films/{film_slug}',
            **shared_meta,
            'property=.og:title.': f'{film.title} - Blender Cloud',
            'name=.twitter:title.': f'{film.title} - Blender Cloud',
            'property=.og:description.': film.description,
            'name=.twitter:description.': film.description,
            'property=.og:image.': 'fakestorage://thumbnail/path.jpg',
            'name=.twitter:image.': 'fakestorage://thumbnail/path.jpg',
        }.items():
            self.assertMetaEquals(html, meta, value)

    def test_film_gallery(self, mock_get_thumbnail):
        film_slug = 'coffee-run'
        film = FilmFactory(slug=film_slug)
        page_url = reverse('film-gallery', kwargs={'film_slug': film_slug})
        mock_get_thumbnail.return_value.url = 'fakestorage://thumbnail/path.jpg'

        response = self.client.get(page_url + '?foo=bar')

        self.assertEqual(response.status_code, 200)
        html = response.content

        self.assertCanonicalLinkEquals(html, f'http://testserver/films/{film_slug}/gallery')
        for meta, value in {
            'property=.og:url.': f'http://testserver/films/{film_slug}/gallery',
            **shared_meta,
            'property=.og:title.': f'{film.title} - Blender Cloud',
            'name=.twitter:title.': f'{film.title} - Blender Cloud',
            'property=.og:description.': film.description,
            'name=.twitter:description.': film.description,
            'property=.og:image.': 'fakestorage://thumbnail/path.jpg',
            'name=.twitter:image.': 'fakestorage://thumbnail/path.jpg',
        }.items():
            self.assertMetaEquals(html, meta, value)

    @patch('static_assets.models.static_assets.get_thumbnail')
    def test_film_gallery_asset(self, mock_get_thumbnail1, mock_get_thumbnail2):
        film_slug = 'coffee-run'
        film = FilmFactory(slug=film_slug)
        asset = AssetFactory(film=film, static_asset=StaticAssetFactory())
        page_url = reverse('film-gallery', kwargs={'film_slug': film_slug})
        mock_get_thumbnail1.return_value.url = 'fakestorage://thumbnail/path.jpg'
        mock_get_thumbnail2.return_value.url = 'fakestorage://thumbnail/path.jpg'

        response = self.client.get(page_url + f'?asset={asset.pk}&foo=bar')

        self.assertEqual(response.status_code, 200)
        html = response.content

        self.assertCanonicalLinkEquals(
            html,
            f'http://testserver/films/{film_slug}/{asset.collection.slug}?asset={asset.pk}',
        )
        for meta, value in {
            'property=.og:url.':
            # TODO(anna): should be gallery URL, not collection?
            f'http://testserver/films/{film_slug}/{asset.collection.slug}?asset={asset.pk}',
            **shared_meta,
            'property=.og:title.': f'{film.title} - {asset.collection.name}: {asset.name} - Blender Cloud',
            'name=.twitter:title.': f'{film.title} - {asset.collection.name}: {asset.name} - Blender Cloud',
            'property=.og:description.': asset.description,
            'name=.twitter:description.': asset.description,
            'property=.og:image.': 'fakestorage://thumbnail/path.jpg',
            'name=.twitter:image.': 'fakestorage://thumbnail/path.jpg',
        }.items():
            self.assertMetaEquals(html, meta, value)

    @patch('static_assets.models.static_assets.get_thumbnail')
    def test_film_gallery_collection(self, mock_get_thumbnail1, mock_get_thumbnail2):
        film_slug = 'coffee-run'
        film = FilmFactory(slug=film_slug)
        asset = AssetFactory(film=film, static_asset=StaticAssetFactory())
        page_url = reverse(
            'collection-detail',
            kwargs={
                'film_slug': film_slug,
                'collection_slug': asset.collection.slug,
            },
        )
        mock_get_thumbnail1.return_value.url = 'fakestorage://thumbnail/path.jpg'
        mock_get_thumbnail2.return_value.url = 'fakestorage://thumbnail/path.jpg'

        response = self.client.get(page_url + '?foo=bar')

        self.assertEqual(response.status_code, 200)
        html = response.content

        self.assertCanonicalLinkEquals(
            html,
            f'http://testserver/films/{film_slug}/{asset.collection.slug}',
        )
        for meta, value in {
            'property=.og:url.': f'http://testserver/films/{film_slug}/{asset.collection.slug}',
            **shared_meta,
            'property=.og:title.': f'{film.title} - {asset.collection.name} - Blender Cloud',
            'name=.twitter:title.': f'{film.title} - {asset.collection.name} - Blender Cloud',
            'property=.og:description.': asset.collection.text,
            'name=.twitter:description.': asset.collection.text,
            'property=.og:image.': 'fakestorage://thumbnail/path.jpg',
            'name=.twitter:image.': 'fakestorage://thumbnail/path.jpg',
        }.items():
            self.assertMetaEquals(html, meta, value)

    @patch('static_assets.models.static_assets.get_thumbnail')
    def test_film_gallery_collection_empty_text_and_name(
        self, mock_get_thumbnail1, mock_get_thumbnail2
    ):
        film_slug = 'coffee-run'
        film = FilmFactory(slug=film_slug)
        asset = AssetFactory(
            film=film,
            static_asset=StaticAssetFactory(),
            collection__text='',
            collection__name='',
        )
        page_url = reverse(
            'collection-detail',
            kwargs={
                'film_slug': film_slug,
                'collection_slug': asset.collection.slug,
            },
        )
        mock_get_thumbnail1.return_value.url = 'fakestorage://thumbnail/path.jpg'
        mock_get_thumbnail2.return_value.url = 'fakestorage://thumbnail/path.jpg'

        response = self.client.get(page_url + '?foo=bar')

        self.assertEqual(response.status_code, 200)
        html = response.content

        self.assertCanonicalLinkEquals(
            html,
            f'http://testserver/films/{film_slug}/{asset.collection.slug}',
        )
        for meta, value in {
            'property=.og:url.': f'http://testserver/films/{film_slug}/{asset.collection.slug}',
            **shared_meta,
            'property=.og:title.': f'{film.title} - {asset.collection.name} - Blender Cloud',
            'name=.twitter:title.': f'{film.title} - {asset.collection.name} - Blender Cloud',
            'property=.og:description.': film.description,
            'name=.twitter:description.': film.description,
            'property=.og:image.': 'fakestorage://thumbnail/path.jpg',
            'name=.twitter:image.': 'fakestorage://thumbnail/path.jpg',
        }.items():
            self.assertMetaEquals(html, meta, value)

    @patch('static_assets.models.static_assets.get_thumbnail')
    def test_film_gallery_collection_asset(self, mock_get_thumbnail1, mock_get_thumbnail2):
        film_slug = 'coffee-run'
        film = FilmFactory(slug=film_slug)
        asset = AssetFactory(film=film, static_asset=StaticAssetFactory())
        page_url = reverse(
            'collection-detail',
            kwargs={
                'film_slug': film_slug,
                'collection_slug': asset.collection.slug,
            },
        )
        mock_get_thumbnail1.return_value.url = 'fakestorage://thumbnail/path.jpg'
        mock_get_thumbnail2.return_value.url = 'fakestorage://thumbnail/path.jpg'

        response = self.client.get(page_url + f'?asset={asset.pk}&foo=bar')

        self.assertEqual(response.status_code, 200)
        html = response.content

        self.assertCanonicalLinkEquals(
            html,
            f'http://testserver/films/{film_slug}/{asset.collection.slug}?asset={asset.pk}',
        )
        for meta, value in {
            'property=.og:url.': f'http://testserver/films/{film_slug}/{asset.collection.slug}?asset={asset.pk}',
            **shared_meta,
            'property=.og:title.': f'{film.title} - {asset.collection.name}: {asset.name} - Blender Cloud',
            'name=.twitter:title.': f'{film.title} - {asset.collection.name}: {asset.name} - Blender Cloud',
            'property=.og:description.': asset.description,
            'name=.twitter:description.': asset.description,
            'property=.og:image.': 'fakestorage://thumbnail/path.jpg',
            'name=.twitter:image.': 'fakestorage://thumbnail/path.jpg',
        }.items():
            self.assertMetaEquals(html, meta, value)

    @patch('static_assets.models.static_assets.get_thumbnail')
    def test_blog_post(self, mock_get_thumbnail1, mock_get_thumbnail2):
        post = PostFactory()
        revision = RevisionFactory(post=post)
        page_url = reverse('post-detail', kwargs={'post_slug': post.slug})
        mock_get_thumbnail1.return_value.url = 'fakestorage://thumbnail/path.jpg'
        mock_get_thumbnail2.return_value.url = 'fakestorage://thumbnail/path.jpg'

        response = self.client.get(page_url + '?foo=bar')

        self.assertEqual(response.status_code, 200)
        html = response.content

        self.assertCanonicalLinkEquals(
            html,
            f'http://testserver/blog/{post.slug}',
        )
        for meta, value in {
            'property=.og:url.': f'http://testserver/blog/{post.slug}',
            **shared_meta,
            'property=.og:title.': f'{revision.title} - Blender Cloud',
            'name=.twitter:title.': f'{revision.title} - Blender Cloud',
            'property=.og:description.': revision.description,
            'name=.twitter:description.': revision.description,
            'property=.og:image.': 'fakestorage://thumbnail/path.jpg',
            'name=.twitter:image.': 'fakestorage://thumbnail/path.jpg',
        }.items():
            self.assertMetaEquals(html, meta, value)
