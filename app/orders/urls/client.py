from django.urls import path

from orders.api.client.views import coupons
from orders.api.pos.views import orders

urlpatterns = [
    path("", orders.POSOrderListView.as_view(), name="list"),
    path("apply_coupon/", coupons.OrderApplyCouponView.as_view(), name="apply-coupon"),
]
