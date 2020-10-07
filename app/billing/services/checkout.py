from typing import List, Optional

from rest_framework.request import Request

from billing.models import Card, Invoice
from billing.serializers.checkout import CheckoutAddressSerializer, CheckoutUserSerializer
from billing.stripe_helper import StripeHelper
from core.services.main_attribute import MainAttributeService
from locations.models import Address
from users.models import Client


class CheckoutService:
    def __init__(self, client: Client, request: Request, invoice: Invoice):
        self._client = client
        self._request = request
        self._stripe_helper = StripeHelper(client)
        self._invoice = invoice

    def save_card_list(self) -> Optional[List[Card]]:
        if not self._invoice.is_save_card:
            return None

        # we are saving all cards received from Stripe
        # in most cases it is only 1 card.
        payment_method_list = self._stripe_helper.payment_method_list

        for item in payment_method_list:
            card, _ = Card.objects.get_or_create(
                client=self._client,
                stripe_id=item.id,
                defaults={
                    "last": item.card.last4,
                    "expiration_month": item.card.exp_month,
                    "expiration_year": item.card.exp_year,
                },
            )

        return self._client.card_list.all()

    def fill_profile(self, user: dict) -> Client:
        serializer = CheckoutUserSerializer(self._client, data=user, partial=True)

        serializer.is_valid()
        serializer.save()

        return self._client

    def create_main_address(self, address: dict) -> Address:
        return self._create_address(address, "main_address")

    def create_billing_address(self, raw_billing_address: dict, is_same_address: bool) -> Address:
        if is_same_address:
            billing_address = self._client.main_address
            self._client.main_billing_address = billing_address
            self._client.save()
        else:
            billing_address = self._create_address(raw_billing_address, "main_billing_address")

        return billing_address

    def _create_address(self, address: dict, attribute: str):
        serializer = CheckoutAddressSerializer(data=address)
        serializer.is_valid()

        service = MainAttributeService(self._request.user.client, attribute)
        address = service.create(serializer)

        return address
