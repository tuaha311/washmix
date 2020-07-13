import logging
import os

import stripe
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from api.legacy.permissions import IsAuthenticatedOrAdmin
from api.legacy.serializers.packages import PackageSerializer
from billing.models import Card
from core.models import Package
from modules.enums import PACKAGES, BalanceOperation
from modules.helpers import update_user_balance, wm_exception
from modules.stripe import StripeHelper
from utilities.email_formatters import format_purchase
from utilities.emails import WMEmailControllerSendGrid

logging.basicConfig(level=logging.ERROR, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Cards(APIView):
    authentication_classes = ()
    permission_classes = (IsAuthenticatedOrAdmin,)

    @wm_exception
    def post(self, request, user=None, **kwargs):
        data_dict = {}
        extra_info = {}
        message = None
        status_api = status.HTTP_200_OK
        transaction_type = kwargs.get("type")
        stripe.api_key = self.load_stripe_config()
        if transaction_type and transaction_type == "add_card":
            message, status_api, extra_info = self.add_card(request, user)
        elif transaction_type == "buy_package":
            message, status_api, extra_info = self.buy_package(request, kwargs.get("id"), user=user)
        data_dict.update({"message": message})
        data_dict.update(extra_info)

        return message, status_api, data_dict

    def load_stripe_config(self):
        return os.environ.get("STRIPE_API_KEY")

    def add_card(self, request, user=None):
        """
        Sample Input Format:
        {
        "card":{
            "token_id": "tok_threeDSecureRequired"
            }
        }
        :param request: 
        :param stripe:
        :param user: it is not NONE if admin or super admin adds a card.
        :return: 
        """
        user = user or request.user
        token = request.get("token_id") or request.data.get("token_id", None)
        card_list = None
        # try:
        message = "User card added!"
        status_api = status.HTTP_201_CREATED

        if not token:
            raise ValidationError(detail="Token id cannot be empty")
        else:
            stripe_obj = StripeHelper()
            if not user.profile.stripe_customer_id:
                # We can save many other attribute on customer object,
                # currently only saving user email.
                customer = stripe_obj.add_customer(user)
                # Tracking stripe user id in profile table for
                # retrieving user for future use.
                profile = user.profile
                if profile:
                    setattr(profile, "stripe_customer_id", customer.id)
                    profile.save()
            else:
                stripe_obj.get_customer(user)
            # Token can be pass from client using stripe.js or Element.
            # Currently creating token at server end.
            # stripe_obj.get_token(card_number, expiry_year, expiry_month)
            stripe_obj.token = token
            # Following line will get you a card against user.
            # Sources on customer against which charge is created e.g Card.
            card = stripe_obj.get_card()
            # Saving Card Id to track multiple added cards against any user.
            card_list = Card.objects.create(user=user, stripe_card_id=card.id)

        response_dict = {"card_id": card_list.id if card_list else None}

        return message, status_api, response_dict

    def charge_user(self, request, card_id):
        """
        This functions buy credit based on user package.
        :param request:
        :param card_id:
        :return:
        """
        stripe_helper = StripeHelper()
        message, status_api, charge = stripe_helper.charge_user(
            request.get("currency"), request.data.get("amount"), card_id, request.user
        )

        return Response(data={"message": message}, content_type="json", status=status_api)

    def buy_package(self, request, card_id, user=None):
        """This function retrieves source(card token) from customer object and create charge
        against token.

        Sample Json Format.
        {"buy_package": {
            "name": "GOLD",
            "currency": "usd"
            }
        }

        """

        user = user or request.user
        try:
            request_body = request.data
        except AttributeError:
            request_body = request

        package_ser = PackageSerializer(
            data=request_body.get("buy_package"), context={"request": self.request}
        )
        package_ser.is_valid(raise_exception=True)

        request_body = request_body.get("buy_package")
        name = PACKAGES[request_body.get("name")]
        try:
            user_package = Package.objects.get(name=name.value)
        except Package.DoesNotExist:
            raise ValidationError(detail="Please populate package by executing addPackage commnand")

        response_dict = {}

        try:
            card = Card.objects.get(user=user, id=card_id)
        except Card.DoesNotExist:
            raise ValidationError(detail="Wrong user card id")

        charge = None
        status_api = status.HTTP_200_OK
        message = "Package added successfully"

        coupon = package_ser.validated_data.get("coupon")
        if PACKAGES.PAYC != name:
            stripe_helper = StripeHelper()
            message, status_api, charge = stripe_helper.charge_user(
                user_package.price,
                request_body.get("currency"),
                card,
                user or request.user,
                metadata={
                    "coupon_code": coupon and coupon.name,
                    "percentage_off": coupon.percentage_off,
                }
                if coupon
                else None,
            )

        if status_api == status.HTTP_200_OK:
            profile = user.profile or self.request.user.profile

            if charge:
                charge_amount = charge.amount / 100

                if coupon:
                    discount = coupon.apply_coupon(charge_amount)
                    charge_amount += discount
                    profile.is_coupon = False
                    profile.save()

            update_user_balance(profile, charge_amount if charge else 0, BalanceOperation.ADD)
            profile.package = user_package
            profile.save()

            if charge:
                WMEmailControllerSendGrid(
                    email_formatter=format_purchase(
                        users=[user or request.user],
                        charge=charge,
                        name=user_package.name,
                    )
                ).send_sendgrid_email()

            response_dict = {
                "card_id": card.id if card else None,
                "name": user_package.name if user_package else None,
                "package_id": user_package.id if user_package else None,
            }

        return message, status_api, response_dict

    @wm_exception
    def patch(self, request, **kwargs):
        """Update user card"""
        if not request.user.is_authenticated:
            message = "Anonymous user"
            status_api = status.HTTP_400_BAD_REQUEST
        elif not kwargs.get("id"):
            message = "Card id is required."
            status_api = status.HTTP_400_BAD_REQUEST
        else:
            # try:
            message = "User card updated!"
            status_api = status.HTTP_200_OK
            user = request.user

            card_id = kwargs.get("id")
            request_body = request.data.get("card", {})

            strip_user_id = user.profile.stripe_customer_id

            Card.objects.filter(user=user).update(is_active=False)
            card_list = Card.objects.get(user=user, id=card_id)
            card_list.is_active = request_body.pop("is_active", False)
            card_list.save()

            if request_body:
                stripe.api_key = self.load_stripe_config()
                customer = stripe.Customer.retrieve(strip_user_id)
                strip_user_card = customer.sources.retrieve(card_list.stripe_card_id)

                for key, val in request_body.items():
                    setattr(strip_user_card, key, val)
                strip_user_card.save()
        return message, status_api, None
