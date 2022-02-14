from django.urls.conf import path, re_path

from static_assets.views import video_progress, coconut_webhook, video_track_view, download_view

urlpatterns = [
    path('api/videos/<int:video_pk>/progress/', video_progress, name='video-progress'),
    # Video Processing webhook
    path('api/videos/<int:video_id>/processing/', coconut_webhook, name='coconut-webhook'),
    # Video tracks served from a different domain require "crossorigin" attribute set on <video>,
    # so tracks are served from the same domain to avoid having CORS set up at the CDN for
    # all the videos as well as tracks.
    # See https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track#attr-src
    re_path(
        r'api/videos/track/(?P<pk>\d+)/(?P<path>\w+/\w+/\w+\.vtt)$',
        video_track_view,
        name='video-track',
    ),
    re_path(
        r'download-source/(?P<source>[a-zA-Z0-9-/.]+)$', download_view, name='download-source-url',
    ),
]
