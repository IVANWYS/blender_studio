from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.shortcuts import render
from django.template.response import HttpResponse
from django.views.decorators.http import require_safe

from common.queries import get_latest_trainings_and_production_lessons
from training import queries
from training.models import Training
from training.views.common import (
    training_model_to_template,
    recently_watched_sections_to_template,
)


@require_safe
def home(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return home_authenticated(request)
    else:
        return home_not_authenticated(request)


@login_required
def home_authenticated(request: HttpRequest) -> HttpResponse:
    favorited_trainings = queries.trainings.favorited(user_pk=request.user.pk)
    recently_watched_sections = queries.sections.recently_watched(user_pk=request.user.pk)
    all_trainings = queries.trainings.all(user_pk=request.user.pk)
    return render(
        request,
        'training/home_authenticated.html',
        context={
            'featured_trainings': Training.objects.filter(is_published=True, is_featured=True)[:3],
            'recently_watched_sections': recently_watched_sections_to_template(
                recently_watched_sections
            ),
            'favorited_trainings': [
                training_model_to_template(training, favorited=True)
                for training in favorited_trainings
            ],
            'all_trainings': all_trainings,
        },
    )


def home_not_authenticated(request: HttpRequest) -> HttpResponse:
    all_trainings = queries.trainings.all(user_pk=None)
    return render(
        request,
        'training/home_not_authenticated.html',
        context={
            'featured_trainings': Training.objects.filter(is_published=True, is_featured=True)[:3],
            'all_trainings': all_trainings,
        },
    )
