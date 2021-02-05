from django.db import models

from core.common_models import Common
from deliveries.choices import DeliveryKind, DeliveryStatus


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

    IMPORTANT: Delivery entity has a signal receiver on `post_save`.
    Signal location - `notifications.signals`
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
    # this invoice is responsible for storing actual amount and
    # discount (at the moment of purchasing), because amount and
    # discount calculated with different business rules for every
    # WashMix services - subscription, basket (POS), delivery
    invoice = models.OneToOneField(
        "billing.Invoice",
        verbose_name="invoice for delivery",
        related_name="delivery",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    note = models.TextField(
        verbose_name="note on delivery",
        blank=True,
    )
    sorting = models.PositiveSmallIntegerField(
        verbose_name="sorting",
        null=True,
        blank=True,
    )
    kind = models.CharField(
        max_length=10,
        verbose_name="kind of delivery",
        choices=DeliveryKind.CHOICES,
        default=DeliveryKind.PICKUP,
    )
    status = models.CharField(
        max_length=20,
        verbose_name="current status",
        choices=DeliveryStatus.CHOICES,
        default=DeliveryStatus.ACCEPTED,
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
        ordering = ["employee", "-date", "sorting", ]
        # for 1 Request we allow 2 Deliveries:
        #   - Pickup
        #   - Dropoff
        unique_together = ["request", "kind",]

    def __str__(self):
        return f"# {self.id}"

    @property
    def pretty_date(self) -> str:
        date = self.date

        pretty_date = date.strftime("%d %B, %Y")

        return pretty_date

    @property
    def order(self):
        request = self.request
        order = request.order

        return order

    @property
    def address(self):
        """
        Delivery address
        """

        request = self.request
        return request.address

    @property
    def client(self):
        """
        Client
        """

        request = self.request
        return request.client

    @property
    def is_rush(self):
        """
        Is rush delivery or not
        """

        request = self.request
        return request.is_rush

    @property
    def comment(self):
        """
        Client clients on delivery
        """

        request = self.request
        return request.comment
