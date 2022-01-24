# noqa: D100
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_safe

from comments.views.common import comments_to_template_type

from stats.models import StaticAssetView
from training import queries
from training.models.progress import UserSectionProgress
from training.types import SectionProgressReportingData
from training.views.common import (
    navigation_to_template,
    training_model_to_template,
)


@require_safe
def section(request: HttpRequest, training_slug: str, section_slug: str) -> HttpResponse:
    """Display a training section or, if section is not found, redirect to a chapter page.

    The redirect is here due to sections and chapters having identical URL format on the old Cloud.
    """
    filter_published = (
        {
            'chapter__is_published': True,
            'chapter__training__is_published': True,
            'is_published': True,
        }
        if not request.user.is_staff and not request.user.is_superuser
        else {}
    )
    result = queries.sections.from_slug(
        user_pk=request.user.pk,
        training_slug=training_slug,
        section_slug=section_slug,
        **filter_published,
    )
    if not result:
        return redirect('chapter', training_slug=training_slug, chapter_slug=section_slug)

    training, training_favorited, chapter, section, maybe_video, comments = result

    if maybe_video is None:
        video = None
    else:
        video, video_start_position = maybe_video
        video.start_position = (
            None if video_start_position is None else video_start_position.total_seconds()
        )

    StaticAssetView.create_from_request(request, section.static_asset_id)
    navigation = queries.trainings.navigation(user_pk=request.user.pk, training_pk=training.pk)

    section_progress_reporting_data = SectionProgressReportingData(
        progress_url=section.progress_url,
        started_timeout=UserSectionProgress.started_duration_pageview_duration.total_seconds(),
        finished_timeout=(
            UserSectionProgress.finished_duration_pageview_duration.total_seconds()
            if video is None
            else None
        ),
    )

    context = {
        'training': training_model_to_template(training, training_favorited),
        'chapter': chapter,
        'section': section,
        'video': video,
        'comments': comments_to_template_type(comments, section.comment_url, user=request.user),
        'section_progress_reporting_data': section_progress_reporting_data,
        'navigation': navigation_to_template(*navigation, user=request.user, current=section),
    }

    return render(request, 'training/section.html', context=context)


@require_safe
def chapter(request: HttpRequest, training_slug: str, chapter_slug: str) -> HttpResponse:
    """Display a training chapter."""
    filter_published = (
        {'training__is_published': True, 'is_published': True,}
        if not request.user.is_staff and not request.user.is_superuser
        else {}
    )
    result = queries.chapters.from_slug(
        user_pk=request.user.pk, training_slug=training_slug, slug=chapter_slug, **filter_published
    )
    if not result:
        return redirect('training', training_slug=training_slug)

    training, training_favorited, chapter = result

    navigation = queries.trainings.navigation(user_pk=request.user.pk, training_pk=training.pk)
    context = {
        'training': training_model_to_template(training, training_favorited),
        'chapter': chapter,
        'navigation': navigation_to_template(*navigation, user=request.user, current=chapter),
    }
    return render(request, 'training/chapter.html', context)
