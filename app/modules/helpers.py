from collections import namedtuple
from enum import Enum
import functools
import logging
import os
import random
import string

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
import stripe
from stripe.error import InvalidRequestError

from error_handling.wm_errors import InternalServerError

logging.basicConfig(level=logging.ERROR, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def prepare_message(pickup_from, pickup_to):
    return "Date: {0}\n Time Range: {1} - {2}".format(
        pickup_from.date().strftime("%Y-%b-%d"),
        pickup_from.time().strftime("%H:%M"),
        pickup_to.time().strftime("%H:%M"),
    )


def mocked_twilio_create(*args):
    pass


def mock_add_customer(*args):
    """
    Mock stripe add customer functionality.
    and returns customer id to save in user.profile table.
    """
    Customer = namedtuple("Customer", "id")
    customer = Customer("sample_id")
    return customer


def mock_get_customer(*args):
    pass


def mock_get_token(*args):
    pass


def mock_get_card(*args):
    """
    Mock adding stripe customer card process and
    returns dummy card object with id.
    """
    Card = namedtuple("Card", "id")
    card = Card("sample_card_id")
    return card


def commit_transaction(obj):
    try:
        obj.save()
    except Exception as e:
        raise InternalServerError("Database transaction failure. Error: {}".format(e.message))


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


class BalanceOperation(Enum):
    ADD = "add"
    DEDUCT = "deduct"
    MANUAL = "manual"


def update_user_balance(profile, amount, bo):
    """
    This functions updates the balance of a user depending on value
    of bo(balance operation). Balance operation is an enum which
    deducts or adds to existing user balance.
    :param profile:
    :param amount:
    :param bo:
    """
    if BalanceOperation.ADD == bo:
        setattr(profile, "balance", profile.balance + amount)
    elif BalanceOperation.DEDUCT == bo:
        if profile.balance - amount <= 0:
            raise ValidationError(detail="Insufficient Balance")
        setattr(profile, "balance", profile.balance - amount)
    profile.save()


def wm_exception(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions
    """

    @functools.wraps(function)
    def wrapper(self, request, **kwargs):
        """
        This decorator handles only stripe defined exceptions and any exception which is subclass from APIException.
        Please do not reply on this decorator for any exception other than above mentioned.
        The idea is to narrow down code for exception handling and bring to the same point.
        """

        message, status_api, data_dict = None, None, {}
        try:
            message, status_api, data_dict = function(self, request, **kwargs)
        except Exception as error:
            if isinstance(error, APIException):
                if isinstance(error.detail, dict):
                    for k, v in error.detail.items():
                        all_errors = ",".join(v)
                        details = all_errors
                else:
                    details = error.detail[0]
            elif isinstance(error, InvalidRequestError):
                details = error.user_message
            else:
                raise ValidationError(detail=error)

            logger.error("Error for {0}, Error Message: {1}".format(request.user.email, details))
            if isinstance(error, APIException):
                raise error
            message = details
            status_api = status.HTTP_400_BAD_REQUEST

        if not data_dict:
            data_dict = {}
        data_dict.update({"message": message})

        return Response(data=data_dict, content_type="json", status=status_api)

    return wrapper


def random_string():
    """Generate a random string with the combination of lowercase and uppercase letters """
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(8))
