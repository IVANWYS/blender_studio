from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework import routers

import blender_id_oauth_client.urls

import blog.urls
import comments.urls
import films.urls
import search.urls
import looper.urls
import subscriptions.urls
import training.urls
import static_assets.urls
import users.urls
import characters.urls
import source_upload.urls
import payments.urls

from common.views.api.markdown_preview import markdown_preview as markdown_preview_view
from common.views.home import home as home_view, welcome as welcome_view
from common.views.home import terms_and_conditions as terms_and_conditions_view, privacy as privacy_view, contact as contact_view, remixing as remixing_view
import common.views.errors as error_views
import static_assets.viewsets
import training.viewsets

# Translation
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog

admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.enable_nav_sidebar = False

router = routers.DefaultRouter(trailing_slash=True)
router.register(r'static-asset', static_assets.viewsets.StaticAssetViewSet)
router.register(r'training/section', training.viewsets.SectionViewSet)
# To leverage the docs boilerplate, a view set is used for single endpoint here too.
router.register(r'upload', static_assets.viewsets.UploadViewSet, basename='upload')
router.get_api_root_view().cls.__name__ = "API"
router.get_api_root_view().cls.__doc__ = "Blender Studio API"


urlpatterns = [
    
    path("i18n/", include("django.conf.urls.i18n")),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', include('loginas.urls')),
    path('admin/', admin.site.urls),
    path('oauth/', include(blender_id_oauth_client.urls)),
    #path('payments/', include((payments.urls, 'payments'), namespace='payments')),
    path('payments/', include(payments.urls)),
]

urlpatterns += i18n_patterns(
    path('', home_view, name='home'),
    path('welcome/', welcome_view, name='welcome'),
    path('comments/', include(comments.urls)),
    path('films/', include(films.urls)),
    path('training/', include(training.urls)),
    path('blog/', include(blog.urls)),
    path('search/', include(search.urls)),
    path('api/markdown-preview', markdown_preview_view, name='api-markdown-preview'),
    path('api/', include((router.urls, 'api'), namespace='api')),
    path('', include(characters.urls)),
    path('looper/', include((looper.urls), namespace='looper')),
    path('source_upload/', include(source_upload.urls)),
    path('', include((subscriptions.urls), namespace='subscriptions')),
    path('', include(users.urls)),
    path('', include(static_assets.urls)),
    path('stats/', include('stats.urls')),
    path('activity/', include('actstream.urls')),
    re_path(r'^webhooks/', include('anymail.urls')),
    path('_nested_admin/', include('nested_admin.urls')),
    
    path('terms-and-conditions/', terms_and_conditions_view, name='terms_and_conditions'),
    path('privacy/', privacy_view, name='privacy'),
    path('contact/', contact_view, name='contact'),
    path('remixing/', remixing_view, name='remixing'),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
)

handler400 = error_views.ErrorView.as_view(template_name='common/errors/400.html', status=400)
handler403 = error_views.ErrorView.as_view(template_name='common/errors/403.html', status=403)
handler404 = error_views.ErrorView.as_view(template_name='common/errors/404.html', status=404)
handler500 = error_views.ErrorView.as_view(template_name='common/errors/500.html', status=500)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Test different error pages by changing the template (400.html, 403.html, etc.)
    urlpatterns += [path('error', TemplateView.as_view(template_name='common/errors/404.html'))]

    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Flatpages catch-all
urlpatterns += [
    re_path(r'^(?P<url>.*/)$', views.flatpage),
]
