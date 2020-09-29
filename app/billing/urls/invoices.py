from django.urls import path

from billing.views import coupons

urlpatterns = [
    # common operation - you can apply coupons at subscription buy scenario
    # or order payment scenario
    path("apply_coupon/", coupons.ApplyCouponView.as_view(), name="apply-coupon"),
]
