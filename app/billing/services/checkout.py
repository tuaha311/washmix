from typing import Tuple

from django.db.transaction import atomic

from rest_framework.request import Request

from api.client.serializers.checkout import (
    WelcomeCheckoutAddressSerializer,
    WelcomeCheckoutUserSerializer,
)
from billing.models import Invoice
from billing.services.card import CardService
from billing.stripe_helper import StripeHelper
from core.services.main_attribute import MainAttributeService
from locations.models import Address
from subscriptions.services.subscription import SubscriptionService
from users.models import Client


class WelcomeService:
    def __init__(self, client: Client, request: Request, order: Invoice):
        self._client = client
        self._request = request
        self._stripe_helper = StripeHelper(client)
        self._order = order

    def checkout(
        self, user: dict, raw_address: dict, raw_billing_address: dict
    ) -> Tuple[Address, dict]:
        client = self._client
        order = self._order
        card_service = CardService(client)
        subscription_service = SubscriptionService(client)

        with atomic():
            if order.is_save_card:
                card_service.save_card_list()

            self._fill_profile(user)
            address = self._create_main_address(raw_address)
            billing_address = self._create_billing_address(raw_billing_address)

            subscription_service.checkout(order)

        return address, billing_address

    def _fill_profile(self, user: dict) -> Client:
        serializer = WelcomeCheckoutUserSerializer(self._client, data=user, partial=True)

        serializer.is_valid()
        serializer.save()

        return self._client

    def _create_main_address(self, raw_address: dict) -> Address:
        return self._create_address(raw_address, "main_address")

    def _create_billing_address(self, raw_billing_address: dict) -> dict:
        client = self._client

        client.billing_address = raw_billing_address

        client.save()

        return client.billing_address

    def _create_address(self, address: dict, attribute: str):
        serializer = WelcomeCheckoutAddressSerializer(data=address)
        serializer.is_valid()

        service = MainAttributeService(self._request.user.client, attribute)
        address = service.create(serializer)

        return address
