from django.db import models

from core.behaviors import Amountable
from core.common_models import Common
from core.mixins import DiscountMixin
from deliveries.common_models import CommonScheduleDelivery


# TODO maybe add invoice
# TODO maybe add status
class Delivery(DiscountMixin, Amountable, CommonScheduleDelivery, Common):
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
        ordering = ["-pickup_date"]

    @property
    def pretty_pickup_message(self) -> str:
        pretty_date = self.pickup_date.strftime("%d %B")

        return pretty_date

    @property
    def discount(self) -> int:
        from orders.utils import get_discount_for_delivery

        return 100
