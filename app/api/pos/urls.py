from django.urls import include, path

app_name = "pos"

urlpatterns = [
    path("basket/", include("orders.urls.baskets")),
    path("orders/", include("orders.urls.orders")),
    path("requests/", include("deliveries.urls")),
]
