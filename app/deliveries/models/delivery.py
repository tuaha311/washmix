from django.db import models

from core.common_models import Common
from deliveries.choices import Kind, Status


class Delivery(Common):
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
    request = models.ForeignKey(
        "deliveries.Request",
        verbose_name="request",
        related_name="delivery_list",
        on_delete=models.CASCADE,
    )
    # invoice created at the moment of Order creation
    invoice = models.OneToOneField(
        "billing.Invoice",
        verbose_name="invoice for delivery",
        related_name="delivery",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    priority = models.PositiveSmallIntegerField(
        verbose_name="priority",
        null=True,
        blank=True,
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
        ordering = ["-date", "-priority"]
        # for 1 Request we allow 2 Deliveries:
        #   - Pickup
        #   - Dropoff
        unique_together = ["request", "kind",]

    def __str__(self):
        return f"# {self.id}"

    @property
    def address(self):
        return self.request.address

    @property
    def client(self):
        return self.request.client

    @property
    def is_rush(self):
        return self.request.is_rush

    @property
    def comment(self):
        return self.request.comment
