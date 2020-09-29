from django.urls import path

from billing.views import checkout, choose, coupons

urlpatterns = [
    # packages and subscription payment views:
    # 1. please, choose a subscription - we will return Invoice.id and attach subscription to Invoice,
    # also, we store this data between screens.
    path("choose/", choose.ChooseView.as_view(), name="choose"),
    # 2. please, if you have a coupon - apply it to the Invoice.id
    # TODO удалить и оставить только в invoices
    path("apply_coupon/", coupons.ApplyCouponView.as_view(), name="apply-coupon"),
    # 3. submit all your personal and address data
    path("checkout/", checkout.CheckoutView.as_view(), name="checkout"),
]
