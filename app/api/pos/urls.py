from django.urls import include, path

from api.pos.views import CouponListView, ItemListView
from orders.urls.pos import basket_urls, order_urls

app_name = "pos"

urlpatterns = [
    path("basket/", include(basket_urls)),
    path("orders/", include(order_urls)),
    path("requests/", include("deliveries.urls.pos")),
    path("items/", ItemListView.as_view(), name="item-list"),
    path("coupons/", CouponListView.as_view(), name="coupon-list"),
]
