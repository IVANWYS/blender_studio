"""Profile activity pages, such as notifications and My activity."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.views.generic import ListView

from actstream import models
from users.models import Notification


class Notifications(LoginRequiredMixin, ListView):
    """Display notifications for an authenticated user."""

    context_object_name = 'notifications'
    model = Notification
    paginate_by = 10
    template_name_suffix = 's'

    def get_queryset(self) -> QuerySet:
        """Return user notifications instead of all notifications."""
        verbs = [_ for _ in self.request.resolver_match.kwargs.get('verbs', '').split(',') if _]
        query = self.request.user.notifications
        return query.filter(action__verb__in=verbs).distinct() if verbs else query.all()


class Activity(LoginRequiredMixin, ListView):
    """Display latest activity of an authenticated user."""

    context_object_name = 'action_list'
    model = models.Action
    paginate_by = 10
    template_name = 'users/activity.html'

    def get_queryset(self) -> QuerySet:
        """Return user activity."""
        return self.request.user.actor_actions.all()
