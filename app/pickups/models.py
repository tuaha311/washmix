from django.db import models

from core.common_models import Common


class Interval(Common):
    """
    Delivery date with start time and end time.
    """

    date = models.DateField(
        verbose_name="date for delivery",
        auto_now_add=True,
    )
    start = models.TimeField(
        verbose_name="start of delivery interval"
    )
    end = models.TimeField(
        verbose_name="end of delivery interval"
    )

    class Meta:
        verbose_name = "delivery interval"
        verbose_name_plural = "delivery intervals"


class Delivery(Common):
    """
    Delivery to / from our Clients.
    """

    # TODO add relation with order in future
    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        related_name="delivery_list",
        on_delete=models.CASCADE,
    )
    address = models.ForeignKey(
        "locations.Address",
        verbose_name="address to pickup and dropoff",
        related_name="delivery_list",
        on_delete=models.SET_NULL,
        null=True,
    )
    pickup_interval = models.ForeignKey(
        "pickups.Interval",
        verbose_name="pickup interval",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
    )
    dropoff_interval = models.ForeignKey(
        "pickups.Interval",
        verbose_name="drop",
        related_name="+",
        on_delete=models.SET,
        null=True,
    )

    class Meta:
        verbose_name = "request pickup"
        verbose_name_plural = "request pickups"
