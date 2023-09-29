import json

from django.contrib.auth.decorators import login_required
from django.http.response import (
    HttpResponse,
    JsonResponse,
    HttpResponseNotAllowed,
    HttpResponseBadRequest,
)
from django.views.decorators.http import require_POST

from common import markdown
from common.shortcodes import render as with_shortcodes


@require_POST
@login_required
def markdown_preview(request) -> HttpResponse:
    """Render a markdown preview, only for editors."""
    if not request.user.is_staff:
        return HttpResponseNotAllowed(['POST'], reason='Markdown preview is not available.')

    request_data = json.loads(request.body)
    if 'markdown' not in request_data:
        return HttpResponseBadRequest('Bad request, missing Markdown.')

    content = markdown.clean(request_data['markdown'])
    md_to_html = markdown.render_unsafe(content)
    final_html = with_shortcodes(md_to_html)
    return JsonResponse({'html': final_html})
