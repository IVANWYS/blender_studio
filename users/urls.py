from django.urls import re_path, path, include

from users.views.activity import Activity, Notifications
from users.views.api import NotificationMarkReadView, NotificationsMarkReadView
from users.views.webhooks import user_modified_webhook
from users.views.account import user_login, user_logout, user_register
import users.views.settings as settings

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', user_register, name='register'),
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
                path('cloud-archive/', settings.CloudArchiveView.as_view(), name='cloud-archive'),
                path('delete/', settings.DeleteView.as_view(), name='user-settings-delete'),
                path('record/', settings.SubscriptionRecord, name='user-settings-record'),
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
