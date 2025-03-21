from django.urls import path

from subscriptions.api.views import checkout, choose

urlpatterns = [
    # 1. please, choose a subscription - we will return Invoice.id and attach subscription to Invoice,
    # also, we store this data between screens.
    path("choose/", choose.SubscriptionChooseView.as_view(), name="choose"),
    # 2. also, you can pay only for subscription
    path("checkout/", checkout.SubscriptionCheckoutView.as_view(), name="checkout"),
]
