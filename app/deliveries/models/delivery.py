from django.db import models

from core.common_models import Common
from deliveries.choices import Kind, Status
from deliveries.common_models import CommonDeliveries


class Delivery(CommonDeliveries, Common):
    """
    Employee-side entity.

    NOTE: Schedule / Delivery uses the same pattern such Package / Subscription.

    Delivery to / from our Clients.
    """

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
    # invoice created at the moment of Order creation
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

    class Meta:
        verbose_name = "delivery"
        verbose_name_plural = "deliveries"
        ordering = ["-date"]

    @property
    def pretty_pickup_message(self) -> str:
        pretty_date = self.date.strftime("%d %B")

        return pretty_date
