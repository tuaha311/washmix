import logging
from typing import Tuple

import stripe
from rest_framework.request import Request
from stripe import Event

from billing.choices import WebhookKind
from billing.containers import PaymentContainer
from billing.services.payments import PaymentService
from billing.validators import validate_stripe_event
from orders.services.order import OrderService
from orders.services.pos import POSService
from subscriptions.services.subscription import SubscriptionService

logger = logging.getLogger(__name__)


class StripeWebhookService:
    enable_ip_check = False
    success_events = ["charge.succeeded"]
    fail_events = ["charge.failed"]

    def __init__(self, request: Request, event: stripe.Event):
        self._request = request
        self._event = event

    def is_valid(self) -> Tuple[bool, dict]:
        """
        Stripe event validity checker.
        """

        request = self._request
        event = self._event
        payment = event.data.object
        enable_ip_check = self.enable_ip_check

        is_valid, errors = validate_stripe_event(payment, request, enable_ip_check)

        return is_valid, errors

    def accept_payment(self, event: Event):
        """
        Main handler that confirms payment and run final hooks
        for order.
        """

        payment_container = self._parse()

        if event.type in self.success_events:
            self._handle_success_events(payment_container)

        elif event.type in self.fail_events:
            self._handle_fail_events(payment_container)

    def _parse(self) -> PaymentContainer:
        """
        Parse Stripe event and retrieve backend entities.
        """

        event = self._event

        payment_container = PaymentContainer(event)

        return payment_container

    def _handle_success_events(self, payment_container: PaymentContainer):
        """
        Handler for success events.
        """

        payment = payment_container.payment
        client = payment_container.client
        invoice = payment_container.invoice
        webhook_kind = payment_container.webhook_kind
        continue_with_order = payment_container.continue_with_order
        order = payment_container.order
        employee = payment_container.employee

        payment_service = PaymentService(client, invoice)
        subscription_service = SubscriptionService(client)

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

            is_replenished = True
            subscription_service.finalize(order, is_replenished)

            pos_service = POSService(client, continue_with_order, employee)
            pos_service.confirm()

        # complex event:
        #   - we are finishing one time payment
        #   - the we are finishin a parent order that create one time payment order
        elif webhook_kind == WebhookKind.REFILL_WITH_CHARGE:
            logger.info("Refill with charge handling")

            pos_service = POSService(client, continue_with_order, employee)
            pos_service.confirm()

    def _handle_fail_events(self, payment_container: PaymentContainer):
        """
        Handler for fail events.
        """

        client = payment_container.client
        webhook_kind = payment_container.webhook_kind
        order = payment_container.order
        continue_with_order = payment_container.continue_with_order

        order_service = OrderService(client)
        subscription_service = SubscriptionService(client)

        if webhook_kind == WebhookKind.SUBSCRIPTION:
            subscription_service.fail(order)

        elif webhook_kind in [
            WebhookKind.SUBSCRIPTION_WITH_CHARGE,
            WebhookKind.REFILL_WITH_CHARGE,
        ]:
            order_service.fail(continue_with_order)
