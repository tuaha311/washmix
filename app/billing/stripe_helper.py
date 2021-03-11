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
        Customer based on our Client's email.
        """

        client = self._client

        try:
            if client.stripe_id:
                # this code can raise InvalidRequestError
                customer = stripe.Customer.retrieve(self._client.stripe_id)
            else:
                customer_list = stripe.Customer.list(email=client.email)
                # this code can raise IndexError
                customer = customer_list["data"][0]

        except (InvalidRequestError, IndexError):
            customer = stripe.Customer.create(
                email=self._client.email,
                metadata={"id": self._client.id},
            )

        return customer

    @property
    def payment_method_list(self) -> List[PaymentMethod]:
        """
        Use this method to retrieve a PaymentMethod for Client.
        """

        payment_method = stripe.PaymentMethod.list(
            customer=self.customer.id,
            type=CARD,
        ).data

        return payment_method

    def create_setup_intent(self):
        """
        Use this method to create CreateIntentView for Stripe.
        Usually, this method called first at card save flow.

        Reference - https://stripe.com/docs/api/setup_intents/create
        """

        setup_intent = stripe.SetupIntent.create(
            customer=self.customer.id,
            usage=SESSION_USAGE,
        )

        return setup_intent

    def create_payment_intent(
        self,
        amount: int,
        metadata: dict,
        currency: str = DEFAULT_CURRENCY,
        payment_method_id: str = None,
    ):
        """
        Use this method to immediately charge saved card on customer.
        Usually, this method called at package billing or order charging.

        Reference - https://stripe.com/docs/api/payment_intents/create
        """

        extra_kwargs = {}
        if payment_method_id:
            extra_kwargs = {
                "payment_method": payment_method_id,
                # these params used only in pair
                "confirm": DEFAULT_CONFIRM,
                "off_session": DEFAULT_OFF_SESSION,
            }

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            receipt_email=self._client.email,
            customer=self.customer.id,
            metadata=metadata,
            **extra_kwargs,
        )

        return payment_intent

    def create_payment_method(self, number: str, exp_month: int, exp_year: int, cvc: str):
        """
        Reference - https://stripe.com/docs/api/payment_methods/create
        """

        payment_method = stripe.PaymentMethod.create(
            card={
                "number": number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc,
            },
            type="card",
            customer=self.customer.id,
        )

        return payment_method

    def detach_payment_method(self, payment_method_id: str):
        """
        Reference - https://stripe.com/docs/api/payment_methods/detach
        """

        payment_method = stripe.PaymentMethod.detach(payment_method_id)

        return payment_method

    def update_customer_info(self, customer_id: str, **kwargs):
        """
        Reference - https://stripe.com/docs/api/customers/update
        """

        customer = stripe.Customer.modify(sid=customer_id, **kwargs)

        return customer
