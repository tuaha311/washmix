from django.urls import path

from orders.api.client.views import coupons
from orders.api.pos.views import checkout, orders

urlpatterns = [
    path("", orders.OrderListView.as_view(), name="list"),
    path("prepare/", orders.OrderPrepareView.as_view(), name="prepare"),
    path("checkout/", checkout.OrderCheckoutView.as_view(), name="checkout"),
    path("repeat/", orders.OrderRepeatView.as_view(), name="repeat"),
    path("apply_coupon/", coupons.OrderApplyCouponView.as_view(), name="apply-coupon"),
]
