from django.db import models

from core.common_models import Common
from orders.choices import PaymentChoices, StatusChoices


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
        null=True,
    )
    request = models.OneToOneField(
        "deliveries.Request",
        verbose_name="request",
        related_name="order",
        on_delete=models.PROTECT,
        null=True,
    )
    subscription = models.OneToOneField(
        "subscriptions.Subscription",
        verbose_name="subscription",
        related_name="order",
        on_delete=models.PROTECT,
        null=True,
    )
    coupon = models.ForeignKey(
        "billing.Coupon",
        verbose_name="coupon",
        related_name="invoice_list",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        verbose_name="status of order",
        choices=StatusChoices.CHOICES,
        default=StatusChoices.ACCEPTED,
    )
    payment = models.CharField(
        max_length=20,
        verbose_name="payment info",
        choices=PaymentChoices.CHOICES,
        default=PaymentChoices.UNPAID,
    )
    note = models.TextField(
        verbose_name="note",
        blank=True,
    )
    is_save_card = models.BooleanField(
        verbose_name="should we save the card",
        default=True,
    )

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
        unique_together = ["basket", "request",]

    @property
    def pretty_status(self):
        return self.get_status_display()
