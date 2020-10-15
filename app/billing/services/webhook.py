from typing import Tuple

from django.conf import settings
from django.db.models import ObjectDoesNotExist

import stripe
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from billing.models import Invoice
from users.models import Client


class StripeWebhookService:
    enable_ip_check = False

    def __init__(self, request: Request, event: stripe.Event):
        self._request = request
        self._event = event
        self._payment = None
        self._invoice = None
        self.status = HTTP_200_OK
        self.body = {}

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

        if self._event.type not in ["payment_intent.succeeded", "charge.succeeded"]:
            return False

        try:
            self._payment = self._event.data.object
            invoice_id = self._payment.metadata.invoice_id
            self._invoice = Invoice.objects.get(pk=invoice_id)
        except ObjectDoesNotExist:
            return False

        return True

    def parse(self) -> Tuple[stripe.PaymentMethod, Client, Invoice, str]:
        client = Client.objects.get(stripe_id=self._payment.customer)
        purpose = getattr(self._payment.metadata, "purpose")

        return self._payment, client, self._invoice, purpose
