from django.db import models

from core.common_models import Common


class Delivery(Common):
    """
    Delivery to / from our Clients.
    """

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
    employee = models.ForeignKey(
        "users.Employee",
        on_delete=models.SET_NULL,
        related_name="delivery_list",
        null=True,
        blank=True,
    )

    comment = models.TextField(
        verbose_name="comment",
        blank=True,
    )
    is_rush = models.BooleanField(
        verbose_name="is a rush / urgent delivery",
        default=False,
    )
    pickup_date = models.DateField(
        verbose_name="date for pickup",
    )
    pickup_start = models.TimeField(
        verbose_name="start of pickup interval"
    )
    pickup_end = models.TimeField(
        verbose_name="end of pickup interval"
    )
    dropoff_date = models.DateField(
        verbose_name="date for dropoff",
    )
    dropoff_start = models.TimeField(
        verbose_name="start of dropoff interval"
    )
    dropoff_end = models.TimeField(
        verbose_name="end of dropoff interval"
    )

    class Meta:
        verbose_name = "delivery"
        verbose_name_plural = "deliveries"
