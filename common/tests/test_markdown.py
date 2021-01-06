from django.test import TestCase

from common.markdown import render_unsafe, render as render_markdown

markdown_html_with_audio_tag = '''
<p class="audio-container">
    <audio controls>
        <source src="http://podcast.blender.institute/media/bip_007_movies1.m4a" type="audio/mp4">
    </audio>
    <a href="http://podcast.blender.institute/media/bip_007_movies1.m4a" download class="btn btn-sm btn-dark">Download</a>
</p>

The first podcast of the year is all about animated movies, including the one we're currently making! We go over the progress on [Caminandes 3](https://cloud.blender.org/p/caminandes-3), the brand new [Character Library](https://cloud.blender.org/p/characters) on Blender Cloud, and finally the topic of the week: Top 3 Animated Movies.

<blockquote><p>hi there, my favorite animated movies are: Bugs, Toy Story and Rango also The Lion King</p> &mdash;  <a href="https://example.com">January 6, 2016</a></blockquote>
'''
markdown_html_with_audio_tag_rendered = '''<p class="audio-container">
    <audio controls>
        <source src="http://podcast.blender.institute/media/bip_007_movies1.m4a" type="audio/mp4">
    </audio>
    <a href="http://podcast.blender.institute/media/bip_007_movies1.m4a" download class="btn btn-sm btn-dark">Download</a>
</p>
<p>The first podcast of the year is all about animated movies, including the one we're currently making! We go over the progress on <a href="https://cloud.blender.org/p/caminandes-3">Caminandes 3</a>, the brand new <a href="https://cloud.blender.org/p/characters">Character Library</a> on Blender Cloud, and finally the topic of the week: Top 3 Animated Movies.</p>
<blockquote><p>hi there, my favorite animated movies are: Bugs, Toy Story and Rango also The Lion King</p> &mdash;  <a href="https://example.com">January 6, 2016</a></blockquote>
'''

markdown_html_with_figure_tag = '''
**Something in bold**

<figure class="figure">
  <img alt="Alt description" class="figure-img img-fluid rounded" src="https://ddz4ak4pa3d19.cloudfront.net/cache/71/d1/71d11574487cb38fd6ace5967ce22a1b.jpg">
  <figcaption class="figure-caption">A caption for the above image.</figcaption>
</figure>
'''

markdown_html_with_figure_tag_rendered = '''<p><strong>Something in bold</strong></p>
<figure class="figure">
  <img alt="Alt description" class="figure-img img-fluid rounded" src="https://ddz4ak4pa3d19.cloudfront.net/cache/71/d1/71d11574487cb38fd6ace5967ce22a1b.jpg">
  <figcaption class="figure-caption">A caption for the above image.</figcaption>
</figure>
'''


class RenderMarkdownTest(TestCase):
    maxDiff = None

    def test_attachment_full_paragraph_link_is_not_urlised(self):
        text = '{attachment 123 link="http://example.com"}'
        self.assertEqual(f'<p>{text}</p>\n', str(render_markdown(text)))

    def test_attachment_part_of_a_paragraph_link_is_not_urlised(self):
        text = 'blah blah {attachment 123 link="http://example.com"} more blah blah'
        self.assertEqual(f'<p>{text}</p>\n', str(render_markdown(text)))

    def test_iframe_full_paragraph_src_is_not_urlised(self):
        text = '{iframe src="http://example.com"}'
        self.assertEqual(f'<p>{text}</p>\n', str(render_markdown(text)))

    def test_iframe_part_of_a_paragraph_src_is_not_urlised(self):
        text = 'blah blah {iframe src=http://example.com} more blah blah'
        self.assertEqual(f'<p>{text}</p>\n', str(render_markdown(text)))

    def test_linkify_urlize_a_link(self):
        text = '**bold** https://example.com'
        self.assertEqual(
            '<p><strong>bold</strong> '
            '<a href="https://example.com">https://example.com</a></p>\n',
            str(render_markdown(text)),
        )

    def test_unsafe_does_not_escape_html_audio_tag(self):
        self.assertEqual(
            markdown_html_with_audio_tag_rendered,
            str(render_unsafe(markdown_html_with_audio_tag)),
        )

    def test_unsafe_does_not_escape_html_figure_with_caption_tag(self):
        self.assertEqual(
            markdown_html_with_figure_tag_rendered,
            str(render_unsafe(markdown_html_with_figure_tag)),
        )
