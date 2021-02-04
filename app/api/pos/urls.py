from django.urls import include, path

from api.pos.views import POSCouponListView, POSItemListView, POSServiceListView
from deliveries.urls import request_urls
from orders.urls.pos import basket_urls, order_urls

app_name = "pos"

urlpatterns = [
    path("basket/", include(basket_urls)),
    path("orders/", include(order_urls)),
    path("items/", POSItemListView.as_view(), name="item-list"),
    path("coupons/", POSCouponListView.as_view(), name="coupon-list"),
    path("services/", POSServiceListView.as_view(), name="service-list"),
    path("requests/", include(request_urls)),
]
