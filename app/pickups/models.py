from django.conf import settings
from django.contrib.postgres.fields import ArrayField
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
    employee = models.ForeignKey(
        "users.Employee",
        on_delete=models.SET_NULL,
        related_name="delivery_list",
        null=True,
        blank=True,
    )
    # can be null only after address removing
    address = models.ForeignKey(
        "locations.Address",
        verbose_name="address to pickup and dropoff",
        related_name="delivery_list",
        on_delete=models.SET_NULL,
        null=True,
    )

    # usual fields
    comment = models.TextField(
        verbose_name="comment",
        blank=True,
    )
    is_rush = models.BooleanField(
        verbose_name="is a rush / urgent delivery",
        default=False,
    )
    # recurring delivery fields
    days = ArrayField(
        base_field=models.CharField(
            max_length=10,
            verbose_name="day of week",
            choices=settings.DELIVERY_DAY_CHOICES,
        ),
        verbose_name="recurring pickup days",
        max_length=7,
    )
    origin = models.ForeignKey(
        "self",
        verbose_name="origin recurring delivery",
        on_delete=models.SET_NULL,
        related_name="recurring_list",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        verbose_name="status of recurring delivery",
        choices=settings.DELIVERY_STATUS_CHOICES,
    )
    # fields about date and intervals
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

    @property
    def pretty_pickup_message(self) -> str:
        pretty_date = self.pickup_date.strftime("%d %B")

        return pretty_date
