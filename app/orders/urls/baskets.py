from django.urls import path

from orders.api.pos.views import baskets

urlpatterns = [
    # 1. you can view items in basket
    path("", baskets.BasketView.as_view(), name="basket"),
    # 2. add or remove items from basket
    path("change_item/", baskets.BasketChangeItemView.as_view(), name="change-item"),
    # 3. you can clear whole basket
    path("clear/", baskets.BasketClearView.as_view(), name="clear"),
]
