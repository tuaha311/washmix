from typing import Tuple

from django.conf import settings
from django.db.models import ObjectDoesNotExist
from django.db.transaction import atomic

import stripe
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from stripe import Event

from billing.choices import Purpose
from billing.models import Invoice
from billing.services.payments import PaymentService
from orders.services.order import OrderService
from subscriptions.services.subscription import SubscriptionService
from users.models import Client


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
                    "ip": ip_address,
                }
                self.status = HTTP_403_FORBIDDEN
                return False

        try:
            invoice = self.invoice
        except ObjectDoesNotExist:
            return False

        if invoice.is_paid:
            return False

        return True

    def accept_payment(self, event: Event):
        """
        Main handler that confirms payment and run final hooks
        for order.
        """

        payment, client, invoice, purpose = self._parse()
        order = invoice.order

        payment_service = PaymentService(client, invoice)
        subscription_service = SubscriptionService(client)
        order_service = OrderService(client)

        with atomic():
            if event.type in self.success_events:
                # we are marked our invoice as paid
                payment_service.confirm(payment)

                if purpose == Purpose.SUBSCRIPTION:
                    subscription_service.finalize(order)

            elif event.type in self.fail_events:
                if purpose == Purpose.SUBSCRIPTION:
                    subscription_service.fail(order)

                elif purpose == Purpose.BASKET:
                    order_service.fail(order)

    def _parse(self) -> Tuple[stripe.PaymentMethod, Client, Invoice, str]:
        """
        Parse Stripe event and retrieve backend entities.
        """

        payment = self.payment

        client = Client.objects.get(stripe_id=payment.customer)
        purpose = getattr(payment.metadata, "purpose", Purpose.SUBSCRIPTION)

        return payment, client, self.invoice, purpose

    @property
    def payment(self):
        return self._event.data.object

    @property
    def invoice(self):
        payment = self.payment
        invoice_id = payment.metadata.invoice_id
        invoice = Invoice.objects.get(pk=invoice_id)

        return invoice
