from django.urls import path

from billing.api.views import coupons
from orders.api.views import orders

urlpatterns = [
    path("", orders.OrderListView.as_view(), name="list"),
    path("prepare/", orders.OrderPrepareView.as_view(), name="prepare"),
    path("checkout/", orders.OrderCheckoutView.as_view(), name="checkout"),
    path("repeat/", orders.OrderRepeatView.as_view(), name="repeat"),
    path("apply_coupon/", coupons.ApplyCouponView.as_view(), name="apply-coupon"),
]
