from typing import List

import stripe
from stripe.api_resources.payment_method import PaymentMethod
from stripe.error import InvalidRequestError

from users.models import Client

DEFAULT_CURRENCY = "usd"
SESSION_USAGE = "off_session"
CARD = "card"
DEFAULT_CONFIRM = True
DEFAULT_OFF_SESSION = True
PAYMENT_INTENT_KWARGS = {
    # these params used only in pair
    "confirm": DEFAULT_CONFIRM,
    "off_session": DEFAULT_OFF_SESSION,
}


class StripeHelper:
    """
    Wrapper around default stripe's Python SDK which uses our Client model
    for some user identification stuff and that provides some predefined settings.
    """

    def __init__(self, client: Client):
        self._client = client

    @property
    def customer(self):
        """
        Convenient property around Customer that will create or get
        Customer based on our Client's ID.
        """

        try:
            customer = stripe.Customer.retrieve(self._client.stripe_id)
        except InvalidRequestError:
            customer = stripe.Customer.create(
                email=self._client.email, metadata={"id": self._client.id},
            )

        return customer

    @property
    def payment_method_list(self) -> List[PaymentMethod]:
        """
        Use this method to retrieve a PaymentMethod for Client.
        """

        payment_method = stripe.PaymentMethod.list(customer=self.customer.id, type=CARD,).data

        return payment_method

    def create_setup_intent(self):
        """
        Use this method to create CreateIntentView for Stripe.
        Usually, this method called first at card save flow.

        Reference - https://stripe.com/docs/api/setup_intents/create
        """

        setup_intent = stripe.SetupIntent.create(customer=self.customer.id, usage=SESSION_USAGE,)

        return setup_intent

    def create_payment_intent(
        self, amount: int, currency: str = DEFAULT_CURRENCY, payment_method_id: str = None
    ):
        """
        Use this method to immediately charge saved card on customer.
        Usually, this method called at package billing or order charging.

        Reference - https://stripe.com/docs/api/payment_intents/create
        """

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=self.customer.id,
            receipt_email=self._client.email,
            payment_method=payment_method_id,
            **PAYMENT_INTENT_KWARGS,
        )

        return payment_intent

    def create_payment_method(self, number: str, exp_month: int, exp_year: int, cvc: str):
        """
        Reference - https://stripe.com/docs/api/payment_methods/create
        """

        payment_method = stripe.PaymentMethod.create(
            card={"number": number, "exp_month": exp_month, "exp_year": exp_year, "cvc": cvc,},
            type="card",
            customer=self.customer.id,
        )

        return payment_method
