from django.db import models

from core.common_models import Common


class Order(Common):
    """
    Central point of system - where we processing orders and storing all info
    related to the order.
    """

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
    # can be null only after delivery removing
    delivery = models.ForeignKey(
        "pickups.Delivery",
        verbose_name="delivery",
        on_delete=models.SET_NULL,
        null=True,
    )

    # TODO добавить поле total
    # TODO добавить ценовой лог

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
