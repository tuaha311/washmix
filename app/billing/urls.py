from django.urls import path

from billing.v1.views import checkout, coupons, payments

urlpatterns = [
    # billing via Stripe related methods:
    # 1. we are creating CreateIntentView object to link Card.id with Client.id for later processing
    path("create_intent/", payments.CreateIntentView.as_view(), name="setup-intent"),
    # 2. you can apply coupon to some invoice during subscription payment or order creation
    path("apply_coupon/", coupons.ApplyCouponView.as_view(), name="apply-coupon"),
    # 3. submit all your personal and address data
    path("checkout/", checkout.WelcomeCheckoutView.as_view(), name="checkout"),
    # 4. we receive success webhook from Stripe and create an Transaction that finishes payment flow
    path("stripe_webhook/", payments.StripeWebhookView.as_view(), name="stripe-webhook"),
]
