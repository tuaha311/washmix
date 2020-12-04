from typing import Union

from django.db.transaction import atomic

from stripe import PaymentIntent, SetupIntent

from billing.choices import Purpose
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from orders.models import Order


class IntentService:
    def __init__(self, client):
        self._client = client

    def create_intent(self, order: Order, is_save_card: bool) -> Union[PaymentIntent, SetupIntent]:
        client = self._client
        subscription = order.subscription
        amount = subscription.price

        with atomic():
            invoice_service = InvoiceService(client)
            invoice = invoice_service.update_or_create(order, amount, Purpose.SUBSCRIPTION)
            InvoiceService.update_invoice(invoice, is_save_card)

            payment_service = PaymentService(client, invoice)
            intent = payment_service.create_intent()

        return intent
