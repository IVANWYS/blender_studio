"""Profile activity pages, such as notifications and My activity."""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from common.models import TemplateVariable

from payments.models import Subscription, Playment_Record

logger = logging.getLogger(__name__)
User = get_user_model()


class IsSubscribedToNewsletterForm(ModelForm):
    """Change User.is_subscribed_to_newsletter flag."""

    class Meta:
        model = User
        fields = ['is_subscribed_to_newsletter']


class ProfileView(LoginRequiredMixin, TemplateView):
    """Template view for the profile settings."""

    template_name = 'users/settings/profile.html'

    def get_context_data(self):
        context = super().get_context_data()
        # TODO: fix this really bad code
        # if coupon_user_subscribed or coupon_user_not_subscribed are not defined in
        # the TemplateVariables, the page will always consider coupon_user_subscribed to be False
        try:
            context['coupon_user_subscribed'] = TemplateVariable.objects.get(
                key='coupon_user_subscribed'
            )
            context['coupon_user_not_subscribed'] = TemplateVariable.objects.get(
                key='coupon_user_not_subscribed'
            )
        except TemplateVariable.DoesNotExist:
            context['coupon_user_subscribed'] = None
            context['coupon_user_not_subscribed'] = None
        return context


class BillingView(LoginRequiredMixin, TemplateView):
    """Template view for the billing/subscription settings."""

    template_name = 'users/settings/billing.html'


class EmailsView(LoginRequiredMixin, TemplateView):
    """Template view for the email notifications settings."""

    template_name = 'users/settings/emails.html'

    def get_context_data(self):
        """Add form to the context."""
        context = super().get_context_data()
        context['form'] = IsSubscribedToNewsletterForm(instance=self.request.user)
        return context

    def post(self, request):
        """Change User.is_subscribed_to_newsletter flag of logged in user."""
        form = IsSubscribedToNewsletterForm(request.POST, instance=request.user)
        form.save()
        return redirect(reverse('user-settings-emails'))


class ProductionCreditsView(LoginRequiredMixin, TemplateView):
    """View to handle visibility of a user credit for the film."""

    template_name = 'users/settings/production_credits.html'

    def get_context_data(self):
        """Add credits to the context."""
        context = super().get_context_data()
        context['credits'] = self.request.user.production_credits.all()
        return context


class DeleteView(LoginRequiredMixin, TemplateView):
    """Template view where account deletion can be requested."""

    template_name = 'users/settings/delete.html'


class CloudArchiveView(LoginRequiredMixin, TemplateView):
    """Template view where Cloud archive can be downloaded."""

    template_name = 'users/settings/cloud_archive.html'

    def get_context_data(self):
        """Look up the archive file and add it to the context, if it exists."""
        context = super().get_context_data()
        download_url = self.request.user.get_cloud_archive_url()
        context['download_url'] = download_url
        return context

def SubscriptionRecord(request):

    if Subscription.objects.values_list(
            'status').filter(user_id=request.user.id).exists():

        user_status = Subscription.objects.values_list(
            'status').filter(user_id=request.user.id)[0][0]

        user_detail = Subscription.objects.filter(user_id=request.user.id)
    else:
        user_status = "Null"
        user_detail = "Null"

    if Playment_Record.objects.values_list(
            'order_time').order_by('-order_time').filter(user_id=request.user.id).exists():
        records = Playment_Record.objects.order_by('-order_time').filter(user_id=request.user.id)
    else:
        records = "Null"

    context = {
        "records": records,
        "user_status": user_status,
        "user_detail": user_detail,
    }
    records = Playment_Record.objects.filter(user_id=request.user.id)

    return render(request, 'users/settings/record.html', context)