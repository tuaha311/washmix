from typing import Optional, Union

from django.db.transaction import atomic

from stripe import PaymentIntent, PaymentMethod, SetupIntent
from stripe.error import StripeError

from billing.models import Invoice, Transaction
from billing.stripe_helper import StripeHelper
from billing.utils import create_debit
from users.models import Client


class PaymentService:
    def __init__(self, client: Client, invoice: Invoice):
        self._client = client
        self._invoice = invoice
        self._stripe_helper = StripeHelper(client)

    def update_invoice(self, is_save_card: bool):
        self._invoice.is_save_card = is_save_card
        self._invoice.save()

    def create_intent(self) -> Union[SetupIntent, PaymentIntent]:
        helper = StripeHelper(self._client)

        if self._invoice.is_save_card:
            intent = helper.create_setup_intent()
        else:
            intent = helper.create_payment_intent(
                amount=self._invoice.amount, invoice=self._invoice
            )

        return intent

    def charge(self) -> Optional[PaymentMethod]:
        # card will be charged at the frontend side
        # if user doesn't want to save a card
        if not self._invoice.is_save_card:
            return None

        payment = None

        for item in self._client.card_list.all():
            # we are trying to charge the card list of client
            # and we are stopping at first successful attempt
            try:
                payment = self._stripe_helper.create_payment_intent(
                    payment_method_id=item.stripe_id,
                    amount=self._invoice.amount,
                    invoice=self._invoice,
                )

                self._client.main_card = item
                self._client.save()

                # we are exiting from the cycle at first successful attempt
                break

            except StripeError:
                continue

        return payment

    def confirm(self, payment: PaymentMethod) -> Optional[Transaction]:
        # .confirm method works idempotently - if we already marked
        # invoice as paid, than we doesn't make changes
        if self._invoice.is_paid:
            return None

        with atomic():
            transaction = create_debit(
                client=self._client,
                invoice=self._invoice,
                stripe_id=payment.id,
                amount=payment.amount,
                source=payment,
            )

            # don't save a card if it wasn't marked by user
            if not self._invoice.is_save_card:
                self._invoice.card = self._client.main_card
                self._invoice.save()

            self._client.subscription = self._invoice.subscription
            self._client.save()

        return transaction
