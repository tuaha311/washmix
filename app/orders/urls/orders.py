from django.urls import path

from orders.views import orders

urlpatterns = [
    path("checkout/", orders.OrderCheckoutView.as_view(), name="checkout"),
    path("repeat/", orders.OrderRepeatView.as_view(), name="repeat"),
]
