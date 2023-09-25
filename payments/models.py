from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()


class UserStatus(models.TextChoices):
    ACTIVE = 'active', _('Active')
    HOLD = 'hold', _('On Hold')
    EXPIRED = 'expired', _('Expired')


class PlanTypes(models.IntegerChoices):
    M1 = 30, _('1 Month')
    M3 = 90, _('3 Month')
    M6 = 180, _('6 Month')
    Y1 = 365, _('1 Year')


class UserStatus(models.TextChoices):
    ACTIVE = 'active', _('Active')
    HOLD = 'hold', _('On Hold')
    EXPIRED = 'expired', _('Expired')


class PaymentTypes(models.TextChoices):
    CARD = 'card', _('Card')
    ALIPLAY = 'alipay', _('Alipay')
    WECHAT = 'wechat_pay', _('Wechat Pay')
    OTHER = 'other', _('Other')


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stripe_user')
    status = models.CharField(choices=UserStatus.choices, default=UserStatus.ACTIVE, max_length=200)
    plan = models.IntegerField(choices=PlanTypes.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    start_date = models.DateTimeField(default=timezone.now, blank=True)
    payment_date = models.DateTimeField(default=timezone.now, blank=True)
    end_date = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        if self.plan == PlanTypes.M1:
            self.price = 100
        elif self.plan == PlanTypes.M3:
            self.price = 300
        elif self.plan == PlanTypes.M6:
            self.price = 600
        elif self.plan == PlanTypes.Y1:
            self.price = 1200

        if self.end_date <= timezone.now():
            self.status = UserStatus.EXPIRED

        super(Subscription, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)


class Playment_Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_playment_record')
    customer_id = models.CharField(max_length=200, blank=True)
    plan = models.IntegerField(choices=PlanTypes.choices)
    payment_type = models.CharField(choices=PaymentTypes.choices,
                                    default=PaymentTypes.OTHER, max_length=200)
    payment_date = models.DateTimeField(default=timezone.now, blank=True)
    end_date = models.DateTimeField(blank=True)
    payment_intent = models.CharField(max_length=200, blank=True)
    user_email = models.CharField(max_length=200, blank=True)
    receipt_url = models.CharField(max_length=255, blank=True)
    order_time = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return str(self.user)
