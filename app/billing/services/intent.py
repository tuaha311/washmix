from typing import Optional, Union

from django.db.transaction import atomic

from stripe import PaymentIntent, SetupIntent

from billing.choices import InvoicePurpose
from billing.models import Invoice
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from orders.models import Order


class IntentService:
    def __init__(self, client):
        self._client = client

    def create_intent(
        self, order: Optional[Order], is_save_card: bool
    ) -> Union[PaymentIntent, SetupIntent]:
        client = self._client
        # here we are using Invoice model like container for case
        # when client want to bind a new card (without any order)
        invoice = Invoice()

        with atomic():
            if order:
                subscription = order.subscription
                amount = subscription.price

                invoice_service = InvoiceService(client)
                invoice = invoice_service.update_or_create(
                    order, amount, InvoicePurpose.SUBSCRIPTION
                )

            payment_service = PaymentService(client, invoice)
            intent = payment_service.create_intent(is_save_card)

        return intent
