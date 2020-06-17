import blender_id_oauth_client.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import comments.urls
import films.urls
import subscriptions.urls
import training.urls
from common.views.home import home as home_view, welcome as welcome_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oauth/', include(blender_id_oauth_client.urls)),
    path('', home_view, name='home'),
    path('welcome/', welcome_view, name='welcome'),
    path('comments/', include(comments.urls)),
    path('films/', include(films.urls)),
    path('training/', include(training.urls)),
    path('subscriptions/', include(subscriptions.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
