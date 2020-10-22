from django.db import models

from core.common_models import Common
from deliveries.choices import Kind, Status
from deliveries.common_models import CommonScheduleDelivery


class Delivery(CommonScheduleDelivery, Common):
    """
    NOTE: Schedule / Delivery uses the same pattern such Package / Subscription.

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
    schedule = models.ForeignKey(
        "deliveries.Schedule",
        verbose_name="recurring schedule of delivery",
        related_name="delivery_list",
        on_delete=models.SET_NULL,
        null=True
    )
    invoice = models.OneToOneField(
        "billing.Invoice",
        verbose_name="invoice for delivery",
        related_name="delivery",
        on_delete=models.PROTECT,
        null=True,
    )

    kind = models.CharField(
        max_length=10,
        verbose_name="kind of delivery",
        choices=Kind.CHOICES,
        default=Kind.PICKUP,
    )
    status = models.CharField(
        max_length=20,
        verbose_name="current status",
        choices=Status.CHOICES,
        default=Status.ACCEPTED,
    )
    date = models.DateField(
        verbose_name="date for delivery",
    )
    start = models.TimeField(
        verbose_name="start of delivery interval"
    )
    end = models.TimeField(
        verbose_name="end of delivery interval"
    )

    # DEPRECATED
    # fields about date and intervals
    pickup_date = models.DateField(
        verbose_name="date for pickup",
    )
    # DEPRECATED
    pickup_start = models.TimeField(
        verbose_name="start of pickup interval"
    )
    # DEPRECATED
    pickup_end = models.TimeField(
        verbose_name="end of pickup interval"
    )
    # DEPRECATED
    dropoff_date = models.DateField(
        verbose_name="date for dropoff",
    )
    # DEPRECATED
    dropoff_start = models.TimeField(
        verbose_name="start of dropoff interval"
    )
    # DEPRECATED
    dropoff_end = models.TimeField(
        verbose_name="end of dropoff interval"
    )

    class Meta:
        verbose_name = "delivery"
        verbose_name_plural = "deliveries"
        ordering = ["-pickup_date"]

    @property
    def pretty_pickup_message(self) -> str:
        pretty_date = self.pickup_date.strftime("%d %B")

        return pretty_date
