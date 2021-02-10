import logging
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

logger = logging.getLogger(__name__)


class StripeWebhookService:
    enable_ip_check = False
    success_events = ["charge.succeeded"]
    fail_events = ["charge.failed"]
    error_status = HTTP_200_OK

    def __init__(self, request: Request, event: stripe.Event):
        self._request = request
        self._event = event
        self.status = HTTP_200_OK
        self.body: dict = {}

    def accept_payment(self, event: Event):
        """
        Main handler that confirms payment and run final hooks
        for order.
        """

        # TODO REFACTOR
        payment_container = self._parse()
        payment = payment_container.payment
        client = payment_container.client
        invoice = payment_container.invoice
        webhook_kind = payment_container.webhook_kind
        continue_with_order = payment_container.continue_with_order
        order = payment_container.order
        employee = payment_container.employee

        payment_service = PaymentService(client, invoice)
        subscription_service = SubscriptionService(client)
        order_service = OrderService(client)

        if event.type in self.success_events:
            # we are marked our invoice as paid
            payment_service.confirm(payment)

            # set subscription to client, notify client
            #  and mark order as paid
            if webhook_kind == WebhookKind.SUBSCRIPTION:
                logger.info("Subscription invoice handling")

                subscription_service.finalize(order)

            # complex event:
            #   - first of all, we are finishing our subscription purchase
            #   - then we are finishing a parent order that created subscription order
            elif webhook_kind == WebhookKind.SUBSCRIPTION_WITH_CHARGE:
                logger.info("Subscription with charge handling")

                subscription_service.finalize(order)

                pos_service = POSService(client, continue_with_order, employee)
                pos_service.confirm()

            # complex event:
            #   - we are finishing one time payment
            #   - the we are finishin a parent order that create one time payment order
            elif webhook_kind == WebhookKind.REFILL_WITH_CHARGE:
                logger.info("Refill with charge handling")

                pos_service = POSService(client, continue_with_order, employee)
                pos_service.confirm()

        elif event.type in self.fail_events:
            if webhook_kind == WebhookKind.SUBSCRIPTION:
                subscription_service.fail(order)

            elif webhook_kind in [
                WebhookKind.SUBSCRIPTION_WITH_CHARGE,
                WebhookKind.REFILL_WITH_CHARGE,
            ]:
                order_service.fail(order)

    def _parse(self) -> Tuple[stripe.PaymentMethod, Client, Invoice, str, Order]:
        """
        Parse Stripe event and retrieve backend entities.
        """

        payment = self.payment

        client = Client.objects.get(stripe_id=payment.customer)
        webhook_kind = getattr(payment.metadata, "webhook_kind", WebhookKind.SUBSCRIPTION)

        return payment, client, self.invoice, webhook_kind, self.continue_with_order
