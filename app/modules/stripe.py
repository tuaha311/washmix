import os

import stripe
from rest_framework import status

from modules.helpers import logger


class StripeHelper:
    def __init__(self):
        self.stripe = stripe
        self.customer = None
        self.token = None
        self.card = None

    def load_strip_api(self):
        self.stripe.api_key = os.environ.get("STRIPE_API_KEY")

    def add_customer(self, user):
        """
        Creates user on Stripes.
        https://stripe.com/docs/api/python#create_customer
        :param user:
        :return:
        """
        self.customer = self.stripe.Customer.create(email=user.email)
        return self.customer

    def get_customer(self, user):
        """
        Retrieves stripe customer.
        https://stripe.com/docs/api/python#retrieve_customer
        :param user:
        :return:
        """
        self.customer = self.stripe.Customer.retrieve(user.profile.stripe_customer_id)
        return self.customer

    def get_token(self, card_number, expiry_year, expiry_month):
        """
        Creates Token, this can also be created at client side using stripe.js, Element etc.
        https://stripe.com/docs/api/python#create_card_token
        :param card_number:
        :param expiry_year:
        :param expiry_month:
        :return:
        """
        self.token = self.stripe.Token.create(
            card={
                "number": card_number,
                "exp_month": expiry_month,
                "exp_year": expiry_year,
                "cvc": "123",
            }
        )

    def get_card(self):
        """
        Create card against stripe customer.
        https://stripe.com/docs/api/python#create_card
        :return:
        """
        return self.customer.sources.create(source=self.token)

    def get_card_info(self, card_id):
        """
        Create card against stripe customer.
        https://stripe.com/docs/api/python#create_card
        :return:
        """
        return self.customer.sources.retrieve(card_id)

    def charge_user(self, charge_amount, currency, card, user, metadata=None):
        self.load_strip_api()
        try:
            stripe_customer_id = user.profile.stripe_customer_id
            message = "User charged successfully with an amount: {amount}"
            status_api = status.HTTP_200_OK
            charge = None

            if not card:
                message = "Must provide card id"
                status_api = status.HTTP_400_BAD_REQUEST
            elif not stripe_customer_id:
                message = "No card added for User!"
                status_api = status.HTTP_400_BAD_REQUEST
            elif not charge_amount:
                message = "Amount cannot be empty."
                status_api = status.HTTP_400_BAD_REQUEST
            else:
                # Charging user source e.g card.
                charge = self.stripe.Charge.create(
                    customer=stripe_customer_id,
                    # Stripe expect amount to be in cents.
                    amount=int(round(charge_amount) * 100),
                    currency=currency,
                    source=card.stripe_card_id,
                    receipt_email=user.email,
                    metadata=metadata if metadata else None,
                )
        except Exception as error:
            try:
                detail = error.detail[0]
            except AttributeError:
                detail = error.user_message
            logger.error(
                "Error while charging user card {0}, Error Message: {1}".format(user.email, detail)
            )
            message = detail
            status_api = status.HTTP_400_BAD_REQUEST
            charge = None

        return (
            message.format(amount=charge.amount / 100) if charge else message,
            status_api,
            charge,
        )
