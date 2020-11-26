from django.urls import path

from orders.api.client.views import coupons
from orders.api.pos.views import baskets, checkout, orders

basket_urls = (
    [
        # 1. you can view items in basket
        path("", baskets.BasketView.as_view(), name="basket"),
        # 2. add or remove items from basket
        path("change_item/", baskets.BasketChangeItemView.as_view(), name="change-item"),
        # 3. you can clear whole basket
        path("clear/", baskets.BasketClearView.as_view(), name="clear"),
    ],
    "basket",
)

order_urls = (
    [
        path("", orders.OrderListView.as_view(), name="list"),
        path("<int:pk>/", orders.OrderUpdateView.as_view(), name="update"),
        path("prepare/", orders.OrderPrepareView.as_view(), name="prepare"),
        path("checkout/", checkout.OrderCheckoutView.as_view(), name="checkout"),
        path("repeat/", orders.OrderRepeatView.as_view(), name="repeat"),
        path("apply_coupon/", coupons.OrderApplyCouponView.as_view(), name="apply-coupon"),
    ],
    "order",
)
