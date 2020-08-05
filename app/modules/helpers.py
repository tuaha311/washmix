import functools
import logging
import random
import string
from collections import namedtuple

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from stripe.error import InvalidRequestError

from api.exceptions import InternalServerError
from modules.enums import BalanceOperation

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
