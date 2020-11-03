from django.urls import include, path

app_name = "pos"

urlpatterns = [
    path("basket/", include("orders.urls.pos.baskets")),
    path("orders/", include("orders.urls.pos.orders")),
    path("requests/", include("deliveries.urls")),
]
