from django.urls import include, path

from training.views.api.comment import comment
from training.views.api.favorite import favorite
from training.views.api.progress import section_progress  # video_progress tracked in static_asset
from training.views.home import home
from training.views.section import section, chapter
from training.views.training import landing, flatpage

urlpatterns = [
    path('', home, name='training-home'),
    path(
        'api/',
        include(
            [
                path('trainings/<int:training_pk>/favorite/', favorite, name='training-favorite'),
                path(
                    'sections/<int:section_pk>/',
                    include(
                        [
                            path('comment/', comment, name='section-comment'),
                            path('progress/', section_progress, name='section-progress'),
                        ]
                    ),
                ),
            ]
        ),
    ),
    path(
        '<slug:training_slug>/',
        include(
            [
                path('', landing, name='training'),
                path('<slug:section_slug>/', section, name='section'),
                path('chapter/<slug:chapter_slug>/', chapter, name='chapter'),
            ]
        ),
    ),
    path('<slug:training_slug>/pages/<slug:page_slug>/', flatpage, name='training-flatpage'),
]
