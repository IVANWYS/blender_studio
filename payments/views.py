from django.shortcuts import render, redirect, HttpResponse
from static_assets.models import Video, VideoTrack, StaticAsset
from django.contrib import messages
from .models import Subscription, Playment_Record
from datetime import datetime, timedelta
from django.utils import timezone
#from django.views.decorators.http import require_http_methods
import pathlib
import datetime
import time
import re
import json
import os
# Create your views here.
import stripe
from flask import Flask, jsonify, request
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def stripe_payment(request):
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
    
    return render(request, 'payments/stripe.html', context)


def plan_select(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        select_plan = request.POST['select_plan']
        if select_plan == "30":
            select_price = settings.PRODUCT_PRICE_1_MONTH
        elif select_plan == "90":
            select_price = settings.PRODUCT_PRICE_3_MONTH
        elif select_plan == "180":
            select_price = settings.PRODUCT_PRICE_6_MONTH
        elif select_plan == "365":
            select_price = settings.PRODUCT_PRICE_1_YEAR

        checkout_session = stripe.checkout.Session.create(
            
            payment_intent_data={
               "metadata": {
                 "stripe_user": request.user.id,
                 "stripe_plan": request.POST['select_plan'],
               }
            },
            payment_method_types=['alipay', 'wechat_pay', 'card'],
            payment_method_options={
                'wechat_pay': {
                    'client': 'web'
                },
            },
            line_items=[
                {
                    'price': select_price,
                    'quantity': 1,
                },
            ],
            mode='payment',
            customer_creation='always',
            success_url=request.META.get('HTTP_REFERER', '/') + 'payment_successful?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.META.get('HTTP_REFERER', '/') + 'payment_cancelled',
        )
        return redirect(checkout_session.url, code=303)
    return render(request, 'payments/stripe.html')


def payment_successful(request):
    time.sleep(5)
    messages.success(request, 'Successful !')
    return redirect("user-settings-record")


def payment_cancelled(request):
    messages.error(request, 'Payment Cancelled !')
    return redirect("stripe")

# /payments/stripe_webhook/
# @require_http_methods(["POST"])
app = Flask(__name__)
@app.route('/payments/stripe_webhook' , methods=['POST'])
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    #time.sleep(10)
    # payload = request.data
    payload = request.body
    #sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    sig_header = request.headers['STRIPE_SIGNATURE']
    event = None
    print("- POST Webhook -")
    print("- Show : -")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print("Webhook error : ValueError")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("Webhook error : SignatureVerificationError")
        return HttpResponse(status=400)
    
    if event.type == 'payment_intent.succeeded':
        #time.sleep(15)
        payment_intent = event.data.object
        print("Webhook : payment_intent.succeeded")
        print('PaymentIntent was successful!')
        print('payment_intent :')
        print(payment_intent)
        print('payment intent id :')
        print(payment_intent.id)
        print('customer id :')
        payment_customer = payment_intent.customer
        print(payment_customer)
        print('email :')
        payment_email = payment_intent.charges.data[0]['billing_details']['email']
        print(payment_email)
        print('payment type :')
        payment_type = payment_intent.charges.data[0]['payment_method_details']['type']
        print(payment_type)
        print('receipt_url :')
        receipt_url = payment_intent.charges.data[0]['receipt_url']
        print(receipt_url)
        print('Metadata :')
        stripe_user = int(payment_intent.charges.data[0]['metadata']['stripe_user'])
        print(stripe_user)
        print('Metadata :')
        stripe_plan = payment_intent.charges.data[0]['metadata']['stripe_plan']
        print(stripe_plan)

        if Subscription.objects.values_list(
                'end_date').filter(user_id=stripe_user).exists():
            end_date = Subscription.objects.values_list(
                'end_date').filter(user_id=stripe_user)[0][0]
        else:
            end_date = timezone.now()

        Subscription.objects.update_or_create(user_id=stripe_user, defaults={
            'plan': int(stripe_plan),
            'status': 'active',
            'payment_date': timezone.now(),
            'end_date': end_date + timedelta(days=int(stripe_plan)), })

        if Playment_Record.objects.values_list(
                'order_time').order_by('-order_time').filter(user_id=stripe_user).exists():
            order_time = int(Playment_Record.objects.values_list(
                'order_time').order_by('-order_time').filter(user_id=stripe_user)[0][0]) + 1
            # order_time = int(order_time) + 1
        else:
            order_time = 1

        Playment_Record.objects.update_or_create(user_id=stripe_user, customer_id=payment_customer, plan=int(stripe_plan), payment_type=payment_type, payment_date=timezone.now(
        ), end_date=timezone.now() + timedelta(days=int(stripe_plan)), payment_intent=payment_intent.id, user_email=payment_email, receipt_url=receipt_url, order_time=order_time)

    elif event.type == 'payment_intent.canceled':
        print("Webhook : payment_intent.canceled")
        print("- Close Webhook - ")
        #print("Webhook : payment_intent.payment_failed")
    elif event.type == 'payment_intent.created':
        print("Webhook : payment_intent.created")
        print("- Close Webhook - ")

    else:
        #print('Unhandled event type {}'.format(event['type']))
        print('Unhandled event type {}'.format(event.type))
        print("Webhook : Unhandled event type")

    return HttpResponse(status=200)
