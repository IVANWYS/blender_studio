from django.urls import re_path, path, include

from users.views.activity import Activity, Notifications
from users.views.api import NotificationMarkReadView, NotificationsMarkReadView
from users.views.webhooks import user_modified_webhook
import users.views.settings as settings

urlpatterns = [
    path('webhooks/user-modified/', user_modified_webhook, name='webhook-user-modified'),
    re_path(
        r'^notifications/(?:(?P<verbs>[a-z ,]+)/)?',
        Notifications.as_view(),
        name='user-notification',
    ),
    path('activity/', Activity.as_view(), name='user-activity'),
    path(
        'settings/',
        include(
            [
                path('profile/', settings.ProfileView.as_view(), name='user-settings'),
                path('billing/', settings.BillingView.as_view(), name='user-settings-billing'),
                path('emails/', settings.EmailsView.as_view(), name='user-settings-emails'),
                path(
                    'production-credits/',
                    settings.ProductionCreditsView.as_view(),
                    name='user-settings-production-credits',
                ),
                path('delete/', settings.DeleteView.as_view(), name='user-settings-delete'),
            ]
        ),
    ),
    path(
        'api/notifications/',
        include(
            [
                path(
                    '<int:pk>/mark-read/',
                    NotificationMarkReadView.as_view(),
                    name='api-notification-mark-read',
                ),
                path(
                    'mark-read/',
                    NotificationsMarkReadView.as_view(),
                    name='api-notifications-mark-read',
                ),
            ]
        ),
    ),
]
