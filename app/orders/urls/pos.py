from django.urls import path

from orders.api.pos.views import baskets, checkout, coupons, orders

basket_urls = (
    [
        # 1. you can view items in basket
        path("", baskets.POSBasketView.as_view(), name="basket"),
        # 2. add or remove items from basket
        path("change_item/", baskets.POSBasketChangeItemView.as_view(), name="change-item"),
        # 3. you can clear whole basket
        path("clear/", baskets.POSBasketClearView.as_view(), name="clear"),
        # 4. you can also add extra custom items to basket
        path(
            "set_extra_items/", baskets.POSBasketSetExtraItemsView.as_view(), name="set-extra-items"
        ),
    ],
    "basket",
)

order_urls = (
    [
        path("prepare/", orders.POSOrderPrepareView.as_view(), name="prepare"),
        path("<int:pk>/", orders.POSOrderUpdateView.as_view(), name="update"),
        path("checkout/", checkout.POSOrderCheckoutView.as_view(), name="checkout"),
        path("apply_coupon/", coupons.POSOrderApplyCouponView.as_view(), name="apply-coupon"),
        path("remove_coupon/", coupons.POSOrderRemoveCouponView.as_view(), name="remove-coupon"),
    ],
    "order",
)
