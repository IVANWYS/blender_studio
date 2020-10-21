"""Shortcode rendering.

Shortcodes are little snippets between curly brackets, which can be rendered
into HTML. Markdown passes such snippets unchanged to its HTML output, so this
module assumes its input is HTML-with-shortcodes.

See mulholland.xyz/docs/shortcodes/.

{iframe src='http://hey' has-cap='subscriber'}

NOTE: nested braces fail, so something like {shortcode abc='{}'} is not
supported.

NOTE: only single-line shortcodes are supported for now, due to the need to
pass them though Markdown unscathed.
"""
import html as html_module  # I want to be able to use the name 'html' in local scope.
import logging
import re
import typing
import urllib.parse

import shortcodes

_parser: shortcodes.Parser = None
_commented_parser: shortcodes.Parser = None
log = logging.getLogger(__name__)


def shortcode(name: str):
    """Class decorator for shortcodes."""

    def decorator(decorated):
        assert hasattr(decorated, '__call__'), '@shortcode should be used on callables.'
        if isinstance(decorated, type):
            as_callable = decorated()
        else:
            as_callable = decorated
        shortcodes.register(name)(as_callable)
        return decorated

    return decorator


class capcheck:
    """Decorator for shortcodes.

    On call, check for capabilities before calling the function. If the user does not
    have a capability, display a message insdead of the content.

    kwargs:
        - 'cap': Capability required for viewing.
        - 'nocap': Optional, text shown when the user does not have this capability.
        - others: Passed to the decorated shortcode.
    """

    def __init__(self, decorated):
        """Initialise the decorator."""
        assert hasattr(decorated, '__call__'), '@capcheck should be used on callables.'
        if isinstance(decorated, type):
            as_callable = decorated()
        else:
            as_callable = decorated
        self.decorated = as_callable

    def __call__(
        self,
        context: typing.Any,
        content: str,
        pargs: typing.List[str],
        kwargs: typing.Dict[str, str],
    ) -> str:
        """Check user for subscription status, roles etc."""
        # TODO(anna) check request.user for groups, subscriber status etc.
        current_user = None
        cap = kwargs.pop('cap', '')
        if cap:
            nocap = kwargs.pop('nocap', '')
            if not current_user.has_cap(cap):
                if not nocap:
                    return ''
                html = html_module.escape(nocap)
                return f'<p class="shortcode nocap">{html}</p>'

        return self.decorated(context, content, pargs, kwargs)


@shortcode('test')
@capcheck
class Test:
    # noqa: D101
    def __call__(
        self,
        context: typing.Any,
        content: str,
        pargs: typing.List[str],
        kwargs: typing.Dict[str, str],
    ) -> str:
        """Just for testing.

        "{test abc='def'}" → "<dl><dt>test</dt><dt>abc</dt><dd>def</dd></dl>"
        """
        parts = ['<dl><dt>test</dt>']

        e = html_module.escape
        parts.extend([f'<dt>{e(key)}</dt><dd>{e(value)}</dd>' for key, value in kwargs.items()])
        parts.append('</dl>')
        return ''.join(parts)


@shortcode('youtube')
@capcheck
class YouTube:
    # noqa: D101
    log = log.getChild('YouTube')

    def video_id(self, url: str) -> str:
        """Find the video ID from a YouTube URL.

        :raise ValueError: when the ID cannot be determined.
        """
        if re.fullmatch(r'[a-zA-Z0-9_\-]+', url):
            return url

        try:
            parts = urllib.parse.urlparse(url)
            if parts.netloc == 'youtu.be':
                return parts.path.split('/')[1]
            if parts.netloc in {'www.youtube.com', 'youtube.com'}:
                if parts.path.startswith('/embed/'):
                    return parts.path.split('/')[2]
                if parts.path.startswith('/watch'):
                    qs = urllib.parse.parse_qs(parts.query)
                    return qs['v'][0]
        except (ValueError, IndexError, KeyError):
            pass

        raise ValueError(f'Unable to parse YouTube URL {url!r}')

    def __call__(
        self,
        context: typing.Any,
        content: str,
        pargs: typing.List[str],
        kwargs: typing.Dict[str, str],
    ) -> str:
        """Embed a YouTube video.

        The first parameter must be the YouTube video ID or URL. The width and
        height can be passed in the equally named keyword arguments.
        """
        width = kwargs.get('width', '560')
        height = kwargs.get('height', '315')

        # Figure out the embed URL for the video.
        try:
            youtube_src = pargs[0]
        except IndexError:
            return html_module.escape('{youtube missing YouTube ID/URL}')

        try:
            youtube_id = self.video_id(youtube_src)
        except ValueError as ex:
            return html_module.escape('{youtube %s}' % "; ".join(ex.args))
        except Exception:
            return html_module.escape('{youtube missing YouTube ID/URL}')
        if not youtube_id:
            return html_module.escape('{youtube invalid YouTube ID/URL}')

        src = f'https://www.youtube.com/embed/{youtube_id}?rel=0'
        html = (
            f'<div class="embed-responsive embed-responsive-16by9">'
            f'<iframe class="shortcode youtube embed-responsive-item"'
            f' width="{width}" height="{height}" src="{src}"'
            f' frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>'
            f'</div>'
        )
        return html


@shortcode('iframe')
@capcheck
def iframe(
    context: typing.Any, content: str, pargs: typing.List[str], kwargs: typing.Dict[str, str]
) -> str:
    """Show an iframe to users with the required capability.

    kwargs:
        - 'cap': Capability required for viewing.
        - others: Turned into attributes for the iframe element.
    """
    import xml.etree.ElementTree as ET

    kwargs['class'] = f'shortcode {kwargs.get("class", "")}'.strip()
    element = ET.Element('iframe', kwargs)
    html = ET.tostring(element, encoding='unicode', method='html', short_empty_elements=True)
    return html


@shortcode('attachment')
@capcheck
class Attachment:
    # noqa: D101

    def __call__(
        self,
        context: typing.Any,
        content: str,
        pargs: typing.List[str],
        kwargs: typing.Dict[str, str],
    ) -> str:
        # noqa: D102
        # TODO(anna) implement attachments
        return '{attachment not implemented}'


def _get_parser() -> typing.Tuple[shortcodes.Parser, shortcodes.Parser]:
    """Return the shortcodes parser, create it if necessary."""
    global _parser, _commented_parser
    if _parser is None:
        start, end = '{}'
        _parser = shortcodes.Parser(start, end)
        _commented_parser = shortcodes.Parser(f'<!-- {start}', f'{end} -->')
    return _parser, _commented_parser


def render_commented(text: str, context: typing.Any = None) -> str:
    """Parse and render HTML-commented shortcodes.

    Expects shortcodes like "<!-- {shortcode abc='def'} -->", as output by
    escape_html().
    """
    _, parser = _get_parser()

    # TODO(Sybren): catch exceptions and handle those gracefully in the response.
    try:
        return parser.parse(text, context)
    except shortcodes.InvalidTagError as ex:
        return html_module.escape('{%s}' % ex)
    except shortcodes.RenderingError as ex:
        log.info('Error rendering tag', exc_info=True)
        return html_module.escape('{unable to render tag: %s}' % str(ex.__cause__ or ex))


def render(text: str, context: typing.Any = None) -> str:
    """Parse and render shortcodes."""
    parser, _ = _get_parser()

    # TODO(Sybren): catch exceptions and handle those gracefully in the response.
    return parser.parse(text, context)


def comment_shortcodes(html: str) -> str:
    r"""Escape shortcodes in HTML comments.

    This is required to pass the shortcodes as-is through Markdown. Render the
    shortcodes afterwards with render_commented().

    >>> comment_shortcodes("text\\n{shortcode abc='def'}\\n")
    "text\\n<!-- {shortcode abc='def'} -->\\n"
    """
    parser, _ = _get_parser()
    return parser.regex.sub(r'<!-- \g<0> -->', html)
