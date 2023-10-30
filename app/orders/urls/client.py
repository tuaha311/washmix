from django.urls import path

from orders.api.client.views import coupons, orders

urlpatterns = [
    path("", orders.OrderListView.as_view(), name="list"),
    path("apply_coupon/", coupons.OrderApplyCouponView.as_view(), name="apply-coupon"),
    path("remove_coupon/", coupons.OrderRemoveCouponView.as_view(), name="remove-coupon"),
    path("<int:pk>/", orders.OrderRetrieveView.as_view(), name="order-detail"),
]
