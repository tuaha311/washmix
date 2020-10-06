from django.urls import path

from orders.views import basket

urlpatterns = [
    # 1. you can view items in basket
    path("", basket.BasketView.as_view(), name="basket"),
    # 2. add or remove items from basket
    path("change_item/", basket.ChangeItemView.as_view(), name="change-item"),
    # 3. you can clear whole basket
    path("clear/", basket.ClearView.as_view(), name="clear"),
    # 4. checkout
    path("checkout/", basket.CheckoutView.as_view(), name="checkout"),
]
