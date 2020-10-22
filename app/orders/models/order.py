from django.db import models

from core.common_models import Common


# TODO maybe add status
class Order(Common):
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
        on_delete=models.PROTECT,
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
        "deliveries.Delivery",
        verbose_name="delivery",
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"

    @property
    def amount(self):
        return self.basket.amount

    @property
    def dollar_amount(self):
        return self.basket.dollar_amount
