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
    # invoice created at the moment of Order creation
    # this invoice is responsible for storing actual amount and
    # discount (at the moment of purchasing), because amount and
    # discount calculated with different business rules for every
    # WashMix services - subscription, basket (POS), delivery
    invoice = models.OneToOneField(
        "billing.Invoice",
        verbose_name="invoice for basket",
        related_name="order",
        on_delete=models.CASCADE,
        null=True,
    )
    # this relation used to save a subscription that provided discount
    # on basket and request
    bought_with_subscription = models.ForeignKey(
        "subscriptions.Subscription",
        verbose_name="subscription that used for purchase this order",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
    balance_before_purchase = models.BigIntegerField(
        verbose_name="customer balance before order, in cents (¢)",
        default=0,
    )
    balance_after_purchase = models.BigIntegerField(
        verbose_name="customer balance after order, in cents (¢)",
        default=0,
    )
    note = models.TextField(
        verbose_name="note",
        blank=True,
    )
    is_save_card = models.BooleanField(
        verbose_name="should we save the card",
        default=True,
    )

    unpaid_reminder_email_count = models.PositiveSmallIntegerField(
        verbose_name="Unpaid Order Reminder Email",
        default=0,
        blank=True,
        editable=False,
    )

    unpaid_reminder_email_time = models.DateTimeField(
        verbose_name="Reminder Email Time",
        editable=False,
        blank=True,
        null=True,
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

    def increase_unpaid_reminder_email_count(self):
        self.unpaid_reminder_email_count =self.unpaid_reminder_email_count + 1

    def set_unpaid_order_reminder_email_time(self, time_to_send):
        self.unpaid_reminder_email_time = time_to_send

    @property
    def unpaid_order_reminder_email_time(self):
        return self.unpaid_reminder_email_time

    @property
    def unpaid_order_reminder_count(self):
        return self.unpaid_reminder_email_count