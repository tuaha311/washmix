from typing import Optional

from django.db.models import ObjectDoesNotExist

import stripe

from billing.choices import WebhookKind
from billing.models import Invoice
from orders.models import Order
from users.models import Client, Employee


class PaymentContainer:
    """
    Payment container that parses Stripe.PaymentMethod to basic primitives.
    """

    def __init__(self, event: stripe.Event):
        self._event = event

    @property
    def payment(self):
        event = self._event

        payment = event.data.object

        return payment

    @property
    def client(self) -> Client:
        payment = self.payment

        client = Client.objects.get(stripe_id=payment.customer)

        return client

    @property
    def webhook_kind(self) -> str:
        payment = self.payment

        webhook_kind = getattr(payment.metadata, "webhook_kind", WebhookKind.SUBSCRIPTION)

        return webhook_kind

    @property
    def invoice(self) -> Invoice:
        payment = self.payment
        invoice_id = payment.metadata.invoice_id
        invoice = Invoice.objects.get(pk=invoice_id)

        return invoice

    @property
    def continue_with_order(self) -> Optional[Order]:
        payment = self.payment
        continue_with_order = getattr(payment.metadata, "continue_with_order", None)

        if not continue_with_order:
            return None

        order = Order.objects.get(pk=continue_with_order)

        return order

    @property
    def order(self) -> Optional[Order]:
        invoice = self.invoice

        try:
            # for WebhookKind.REFILL_WITH_CHARGE `order` is None
            order = invoice.order
        except ObjectDoesNotExist:
            order = None

        return order

    @property
    def employee(self) -> Optional[Employee]:
        continue_with_order = self.continue_with_order

        try:
            # for WebhookKind.SUBSCRIPTION `continue_with_order` is None
            employee = continue_with_order.employee
        except AttributeError:
            employee = None

        return employee
