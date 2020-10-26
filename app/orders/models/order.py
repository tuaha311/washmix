from django.conf import settings
from django.db import models

from core.common_models import Common
from orders.choices import Status


class Order(Common):
    """
    Employee-side and Client-side entity.

    Central point of system - where we processing orders and storing all info
    related to the order.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="order_list",
    )
    employee = models.ForeignKey(
        "users.Employee",
        verbose_name="employee who handles this order",
        on_delete=models.SET_NULL,
        related_name="order_list",
        null=True,
        blank=True,
    )
    basket = models.OneToOneField(
        "orders.Basket",
        verbose_name="basket",
        related_name="order",
        on_delete=models.PROTECT,
    )
    request = models.OneToOneField(
        "deliveries.Request",
        verbose_name="request",
        related_name="order",
        on_delete=models.PROTECT,
    )
    invoice_list = models.ManyToManyField(
        "billing.Invoice",
        verbose_name="invoice list",
        related_name="order_list",
    )

    status = models.CharField(
        max_length=20,
        verbose_name="status of order",
        choices=Status.CHOICES,
        default=Status.ACCEPTED,
    )

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
        unique_together = ["basket", "request",]

    @property
    def pretty_status(self):
        return self.get_status_display()
