from typing import Union

from stripe import PaymentIntent, SetupIntent

from billing.models import Invoice
from billing.stripe_helper import StripeHelper
from users.models import Client


class PaymentService:
    def __init__(self, client: Client, invoice: Invoice):
        self._client = client
        self._invoice = invoice

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
