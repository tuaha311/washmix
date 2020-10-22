from django.db import models

from core.common_models import Common
from deliveries.choices import Kind, Status
from deliveries.common_models import CommonDeliveries


class Delivery(CommonDeliveries, Common):
    """
    Employee-side entity.

    Concrete delivery to / from our Clients.
    This entity visible only to employees and back-office.
    Drivers see a feed with new Deliveries and can take it for execution.

    Also, Drivers can filter a feed by:
        - Pickup or Dropoff
        - Date
        - Address
    """

    employee = models.ForeignKey(
        "users.Employee",
        verbose_name="employee that handles this delivery",
        on_delete=models.SET_NULL,
        related_name="delivery_list",
        null=True,
        blank=True,
    )
    # usually, 1 Request creates 2 Delivery:
    #   - for pickup
    #   - for dropoff
    request = models.ForeignKey(
        "deliveries.Request",
        verbose_name="original request from our client",
        related_name="delivery_list",
        on_delete=models.CASCADE,
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
