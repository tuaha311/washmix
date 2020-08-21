from decimal import Decimal

import stripe
from stripe.error import InvalidRequestError

from users.models import Client

DEFAULT_CURRENCY = "usd"
SESSION_USAGE = "off_session"
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
            self._client.stripe_id = customer["id"]
            self._client.save()

        return customer

    def create_setup_intent(self):
        """
        Use this method to create SetupIntent for Stripe.
        Usually, this method called first at card save flow.

        Reference - https://stripe.com/docs/api/setup_intents/create
        """

        setup_intent = stripe.SetupIntent.create(customer=self.customer["id"], usage=SESSION_USAGE,)

        return setup_intent

    def create_payment_intent(self, dollar_amount: Decimal, currency: str = DEFAULT_CURRENCY):
        """
        Use this method to immediately charge saved card on customer.
        Usually, this method called at package billing or order charging.

        Reference - https://stripe.com/docs/api/payment_intents/create
        """

        cent_amount = int(dollar_amount * 100)

        payment_intent = stripe.PaymentIntent.create(
            amount=cent_amount,
            currency=currency,
            customer=self.customer["id"],
            receipt_email=self._client.email,
            **PAYMENT_INTENT_KWARGS,
        )

        return payment_intent
