from django.contrib import admin

from payments.models import Subscription, Playment_Record


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'plan', 'start_date', 'payment_date', 'end_date')
    list_display_links = ('user', 'status', 'plan', 'start_date', 'payment_date', 'end_date')
    search_fields = ('user', 'status')
    list_per_page = 20


admin.site.register(Subscription, SubscriptionAdmin)


class PlaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'customer_id', 'plan', 'payment_type', 'payment_intent', 'order_time',)
    list_display_links = ('user', 'customer_id', 'plan', 'payment_type',
                          'payment_intent', 'order_time',)
    search_fields = ('user', 'customer_id', 'payment_intent', 'payment_type')
    list_per_page = 20


admin.site.register(Playment_Record, PlaymentRecordAdmin)
