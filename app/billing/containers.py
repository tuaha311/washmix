import logging
from dataclasses import dataclass
from typing import Optional, Tuple

from django.conf import settings
from django.db.models import ObjectDoesNotExist

import stripe
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from stripe import Event

from billing.choices import WebhookKind
from billing.models import Invoice
from billing.services.payments import PaymentService
from orders.models import Order
from orders.services.order import OrderService
from orders.services.pos import POSService
from subscriptions.services.subscription import SubscriptionService
from users.models import Client


class PaymentContainer:
    """
    Payment container that parses Stripe.PaymentMethod to basic primitives.
    """

    _event: stripe.Event

    def parse(self) -> Tuple[stripe.PaymentMethod, Client, Invoice, str, Order]:
        """
        Parse Stripe event and retrieve backend entities.
        """

        payment = self.payment

        client = Client.objects.get(stripe_id=payment.customer)
        webhook_kind = getattr(payment.metadata, "webhook_kind", WebhookKind.SUBSCRIPTION)

        return payment, client, self.invoice, webhook_kind, self.continue_with_order

    @property
    def payment(self):
        return self._event.data.object

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
    def order(self):
        invoice = self.invoice

        try:
            # for WebhookKind.REFILL_WITH_CHARGE `order` is None
            order = invoice.order
        except ObjectDoesNotExist:
            order = None

        return order

    @property
    def employee(self):
        continue_with_order = self.continue_with_order

        try:
            # for WebhookKind.SUBSCRIPTION `continue_with_order` is None
            employee = continue_with_order.employee
        except AttributeError:
            employee = None

        return employee
