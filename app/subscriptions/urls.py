from django.urls import path

from subscriptions.v1.views import checkout, choose

urlpatterns = [
    # 1. please, choose a subscription - we will return Invoice.id and attach subscription to Invoice,
    # also, we store this data between screens.
    path("choose_package/", choose.SubscriptionChooseView.as_view(), name="choose_package"),
    # 2. also, you can pay only for subscription
    path("checkout/", checkout.SubscriptionCheckoutView.as_view(), name="checkout"),
]
