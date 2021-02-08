import logging
from typing import Tuple

from django.conf import settings
from django.db.models import ObjectDoesNotExist

import stripe
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from stripe import Event

from billing.choices import InvoicePurpose, WebhookKind
from billing.models import Invoice
from billing.services.payments import PaymentService
from orders.services.order import OrderService
from orders.services.pos import POSService
from subscriptions.services.subscription import SubscriptionService
from users.models import Client

logger = logging.getLogger(__name__)


class StripeWebhookService:
    enable_ip_check = False
    success_events = ["charge.succeeded"]
    fail_events = ["charge.failed"]

    def __init__(self, request: Request, event: stripe.Event):
        self._request = request
        self._event = event
        self.status = HTTP_200_OK
        self.body: dict = {}

    def is_valid(self):
        if self.enable_ip_check:
            ip_address = self._request.META["HTTP_X_FORWARDED_FOR"]

            # don't allowing other IPs excluding Stripe's IPs
            if ip_address not in settings.STRIPE_WEBHOOK_IP_WHITELIST:
                self.body = {
                    "reason": "ip_not_in_whitelist",
                }
                self.status = HTTP_403_FORBIDDEN

                logger.info(f"IP address {ip_address} not in whitelist.")

                return False

        try:
            invoice = self.invoice
        except ObjectDoesNotExist:
            self.body = {
                "reason": "invoice_doesnt_exists",
            }
            self.status = HTTP_403_FORBIDDEN

            logger.info(f"Invoice doesn't exists.")

            return False

        if invoice.is_paid:
            self.body = {
                "reason": "invoice_is_paid",
            }
            self.status = HTTP_403_FORBIDDEN

            logger.info(f"{invoice} is already paid.")

            return False

        return True

    def accept_payment(self, event: Event):
        """
        Main handler that confirms payment and run final hooks
        for order.
        """

        payment, client, invoice, webhook_kind = self._parse()
        order = invoice.order
        parent_order = order.parent
        employee = order.employee

        payment_service = PaymentService(client, invoice)
        subscription_service = SubscriptionService(client)
        order_service = OrderService(client)
        pos_service = POSService(client, parent_order, employee)

        if event.type in self.success_events:
            # we are marked our invoice as paid
            payment_service.confirm(payment)

            # complex event:
            #   - first of all, we are finishing our subscription purchase
            #   - then we are finishing a parent order that created subscription order
            if webhook_kind == WebhookKind.SUBSCRIPTION_WITH_CHARGE:
                logger.info("POS invoice handling")
                subscription_service.finalize(order)
                pos_service.checkout()

            # set subscription to client, notify client
            #  and mark order as paid
            elif webhook_kind == WebhookKind.SUBSCRIPTION:
                logger.info("Subscription invoice handling")
                subscription_service.finalize(order)

            # complex event:
            #   - we are finishing one time payment
            #   - the we are finishin a parent order that create one time payment order
            elif webhook_kind == WebhookKind.REFILL_WITH_CHARGE:
                logger.info("One time refill handling")
                order_service.finalize(order, employee)

        elif event.type in self.fail_events:
            if webhook_kind == WebhookKind.SUBSCRIPTION:
                subscription_service.fail(order)

            elif webhook_kind in [
                WebhookKind.SUBSCRIPTION_WITH_CHARGE,
                WebhookKind.REFILL_WITH_CHARGE,
            ]:
                order_service.fail(order)

    def _parse(self) -> Tuple[stripe.PaymentMethod, Client, Invoice, str]:
        """
        Parse Stripe event and retrieve backend entities.
        """

        payment = self.payment

        client = Client.objects.get(stripe_id=payment.customer)
        webhook_kind = getattr(payment.metadata, "webhook_kind", WebhookKind.SUBSCRIPTION)

        return payment, client, self.invoice, webhook_kind

    @property
    def payment(self):
        return self._event.data.object

    @property
    def invoice(self):
        payment = self.payment
        invoice_id = payment.metadata.invoice_id
        invoice = Invoice.objects.get(pk=invoice_id)

        return invoice
