from django.db import models

from core.common_models import Common
from orders.choices import OrderPaymentChoices, OrderStatusChoices


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
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    request = models.OneToOneField(
        "deliveries.Request",
        verbose_name="request",
        related_name="order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    subscription = models.OneToOneField(
        "subscriptions.Subscription",
        verbose_name="subscription",
        related_name="order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        choices=OrderStatusChoices.CHOICES,
        default=OrderStatusChoices.ACCEPTED,
    )
    payment = models.CharField(
        max_length=20,
        verbose_name="payment info",
        choices=OrderPaymentChoices.CHOICES,
        default=OrderPaymentChoices.UNPAID,
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
        # for one order we can have only one unique pair
        # of (basket_id, request_id)
        unique_together = ["basket", "request",]
        ordering = ["-created"]

    def __str__(self):
        return f"№ {self.pk}"

    @property
    def pretty_status(self):
        return self.get_status_display()

    @property
    def is_all_invoices_paid(self) -> bool:
        basket = self.basket
        subscription = self.subscription
        request = self.request
        pickup = None
        dropoff = None

        if request:
            pickup = request.pickup
            dropoff = request.dropoff

        washmix_paid_services = [basket, subscription, pickup, dropoff]
        invoice_list = [item.invoice for item in washmix_paid_services if item]

        return all([item.is_paid for item in invoice_list])
