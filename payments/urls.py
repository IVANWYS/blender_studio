from django.urls import path
from . import views

#app_name = 'payments'

urlpatterns = [
    path('', views.stripe_payment, name='stripe'),
    path('plan_select', views.plan_select, name='plan_select'),
    path('payment_successful/', views.payment_successful, name='payment_successful'),
    path('payment_cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
]
