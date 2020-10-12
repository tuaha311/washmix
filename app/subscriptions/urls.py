from django.urls import path

from billing.views import checkout
from subscriptions.v1.views import choose

urlpatterns = [
    # packages and subscription payment views:
    # 1. please, choose a subscription - we will return Invoice.id and attach subscription to Invoice,
    # also, we store this data between screens.
    path("choose_package/", choose.ChooseView.as_view(), name="choose_package"),
    # 3. submit all your personal and address data
    path("checkout/", checkout.SubscriptionCheckoutView.as_view(), name="checkout"),
]
