from django.db import models

from core.behaviors import Amountable
from core.common_models import Common


class Order(Amountable, Common):
    """
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
        verbose_name="employee that handles this order",
        on_delete=models.SET_NULL,
        related_name="order_list",
        null=True,
        blank=True,
    )
    invoice = models.OneToOneField(
        "billing.Invoice",
        verbose_name="invoice",
        related_name="order",
        on_delete=models.CASCADE,
    )
    basket = models.OneToOneField(
        "orders.Basket",
        verbose_name="basket",
        related_name="order",
        on_delete=models.CASCADE,
        null=True,
    )
    # can be null only after delivery removing
    delivery = models.ForeignKey(
        "pickups.Delivery",
        verbose_name="delivery",
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
