from django.urls import path

from deliveries.api.pos.views import POSRequestRushAmountView

request_urls = (
    [
        path("rush_amount/", POSRequestRushAmountView.as_view(), name="rush-amount"),
    ],
    "request",
)
