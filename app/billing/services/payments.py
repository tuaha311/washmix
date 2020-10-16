import logging
from typing import Optional, Tuple, Union

from django.db.transaction import atomic

from stripe import PaymentIntent, PaymentMethod, SetupIntent
from stripe.error import StripeError

from billing.models import Invoice, Transaction
from billing.services.card import CardService
from billing.stripe_helper import StripeHelper
from billing.utils import create_credit, create_debit
from users.models import Client

logger = logging.getLogger(__name__)


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

    def create_intent(self) -> Union[SetupIntent, PaymentIntent]:
        """
        This method used to create Stripe's `SetupIntent` or `PaymentIntent` in
        dependency of user preferences:
            - If user want to save card, we create `SetupIntent` to save user's card
            in Stripe and for later billing
            - If user want to make one time payment - we are creating immediate payment entity
            called `PaymentIntent`
        """

        if self._invoice.is_save_card:
            intent = self._stripe_helper.create_setup_intent()
        else:
            intent = self._stripe_helper.create_payment_intent(
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

        with atomic():
            paid_amount, unpaid_amount = self._charge_prepaid_balance()

            if unpaid_amount:
                self._charge_card()

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

        transaction = create_debit(
            client=self._client,
            invoice=self._invoice,
            stripe_id=payment.id,
            amount=payment.amount,
            source=payment,
        )

        return transaction

    def _charge_prepaid_balance(self) -> Tuple[int, int]:
        amount = self._invoice.amount

    def _charge_card(self, amount: int):
        card_service = CardService(self._client, self._invoice)

        for item in self._client.card_list.all():
            # we are trying to charge the card list of client
            # and we are stopping at first successful attempt
            try:
                payment = self._stripe_helper.create_payment_intent(
                    payment_method_id=item.stripe_id, amount=amount, invoice=self._invoice,
                )

                card_service.update_main_card(self._client, item)

                return payment

            except StripeError as err:
                logger.error(err)
                continue
