from django.urls import path

from deliveries.api.pos.views import POSRequestSetRushAmountView

request_urls = (
    [
        path("set_rush_amount/", POSRequestSetRushAmountView.as_view(), name="set-rush-amount"),
    ],
    "request",
)
