from django.urls import path

from orders.api.client.views import coupons
from orders.api.pos.views import orders

urlpatterns = [
    path("", orders.OrderListView.as_view(), name="list"),
    path("repeat/", orders.OrderRepeatView.as_view(), name="repeat"),
    path("apply_coupon/", coupons.OrderApplyCouponView.as_view(), name="apply-coupon"),
]
