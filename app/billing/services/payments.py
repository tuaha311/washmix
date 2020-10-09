from typing import Optional, Union

from django.db.transaction import atomic

from stripe import PaymentIntent, PaymentMethod, SetupIntent
from stripe.error import StripeError

from billing.models import Invoice, Transaction
from billing.services.card import CardService
from billing.stripe_helper import StripeHelper
from billing.utils import create_debit
from users.models import Client


class PaymentService:
    """
    Main payment service, that responsible for accepting and providing billing.

    This service main core capabilities:
        - Save user's card in Stripe
        - Charge user's card immediately
        - Charge user's card later
        - Confirm payment
    """

    def __init__(self, client: Client, invoice: Invoice):
        self._client = client
        self._invoice = invoice
        self._stripe_helper = StripeHelper(client)
        self._card_service = CardService(client, invoice)

    def create_intent(self) -> Union[SetupIntent, PaymentIntent]:
        """
        This method used to create Stripe's `SetupIntent` or `PaymentIntent` in
        dependency of user preferences:
            - If user want to save card, we create `SetupIntent` to save user's card
            in Stripe and for later billing
            - If user want to make one time payment - we are creating immediate payment entity
            called `PaymentIntent`
        """

        helper = StripeHelper(self._client)

        if self._invoice.is_save_card:
            intent = helper.create_setup_intent()
        else:
            intent = helper.create_payment_intent(
                amount=self._invoice.amount, invoice=self._invoice
            )

        return intent

    def charge(self) -> Optional[PaymentMethod]:
        """
        We are iterating to the all user's card list and choosing first one
        where we find an enough money to charge. At first successful attempt we
        are continuing our payment flow.

        In most cases, we are creating `PaymentIntent` under the hood and then waiting for
        web hook event from Stripe to confirm and finish payment flow.
        """

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

                self._card_service.update_main_card(self._client, item)

                # we are exiting from the cycle at first successful attempt
                break

            except StripeError:
                continue

        return payment

    def confirm(self, payment: PaymentMethod) -> Optional[Transaction]:
        """
        Last method in payment flow - it's responsible for creating payment transaction
        for invoice. After transaction created for invoice, Invoice will be marked
        as paid.
        """

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
            if self._invoice.is_save_card:
                self._invoice.card = self._client.main_card
                self._invoice.save()

            self._client.subscription = self._invoice.subscription
            self._client.save()

        return transaction
