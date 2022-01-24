"""Views related to training."""
from django.http.request import HttpRequest
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_safe

from training import queries
from training.views.common import navigation_to_template, training_model_to_template
from training.models import Training, TrainingFlatPage


@require_safe
def landing(request: HttpRequest, training_slug: str):
    """Display a training with a given slug."""
    filter_published = (
        {'is_published': True}
        if not request.user.is_staff and not request.user.is_superuser
        else {}
    )
    result = queries.trainings.from_slug(
        user_pk=request.user.pk, training_slug=training_slug, **filter_published
    )

    if result is None:
        raise Http404
    else:
        training, is_favorited = result
        navigation = queries.trainings.navigation(user_pk=request.user.pk, training_pk=training.pk)
        return render(
            request,
            'training/training.html',
            context={
                'training': training_model_to_template(training, is_favorited),
                'navigation': navigation_to_template(
                    *navigation, user=request.user, current='overview'
                ),
            },
        )


@require_safe
def flatpage(request: HttpRequest, training_slug: str, page_slug: str) -> HttpResponse:
    """Display a training flatpage specified by the given slug."""
    filter_published = (
        {'is_published': True}
        if not request.user.is_staff and not request.user.is_superuser
        else {}
    )
    training = get_object_or_404(Training, slug=training_slug, **filter_published)
    flatpage = get_object_or_404(TrainingFlatPage, training=training, slug=page_slug)
    navigation = queries.trainings.navigation(user_pk=request.user.pk, training_pk=training.pk)
    context = {
        'training': training,
        'flatpage': flatpage,
        'user_can_edit_training': (
            request.user.is_staff and request.user.has_perm('training.change_training')
        ),
        'user_can_edit_flatpage': (
            request.user.is_staff and request.user.has_perm('training.change_trainingflatpage')
        ),
        'navigation': navigation_to_template(*navigation, user=request.user, current=flatpage),
    }
    return render(request, 'training/flatpage.html', context)
