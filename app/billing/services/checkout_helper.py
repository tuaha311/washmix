from django.db.transaction import atomic

from stripe import PaymentIntent

from billing.models import Card, Invoice, Transaction
from users.models import Client


class CheckoutHelper:
    def __init__(self, client: Client):
        self._client = client

    def checkout(self, invoice: Invoice, payment: PaymentIntent, card: Card):
        with atomic():
            transaction = Transaction.objects.create(
                invoice=invoice,
                kind=Transaction.DEBIT,
                provider=Transaction.STRIPE,
                client=self._client,
                stripe_id=payment.id,
                amount=payment.amount,
            )

            invoice.card = card
            invoice.save()

            self._client.subscription = invoice.subscription
            self._client.save()
