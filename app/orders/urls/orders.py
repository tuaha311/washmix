from django.urls import path

from orders.v1.views import orders

urlpatterns = [
    path("", orders.OrderListView.as_view(), name="list"),
    path("checkout/", orders.OrderCheckoutView.as_view(), name="checkout"),
    path("repeat/", orders.OrderRepeatView.as_view(), name="repeat"),
]
