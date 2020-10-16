from rest_framework.request import Request

from billing.models import Invoice
from billing.stripe_helper import StripeHelper
from billing.v1.serializers.checkout import (
    WelcomeCheckoutAddressSerializer,
    WelcomeCheckoutUserSerializer,
)
from core.services.main_attribute import MainAttributeService
from locations.models import Address
from subscriptions.services.subscription import SubscriptionService
from users.models import Client


class WelcomeCheckoutService:
    def __init__(self, client: Client, request: Request, invoice: Invoice):
        self._client = client
        self._request = request
        self._stripe_helper = StripeHelper(client)
        self._invoice = invoice

    def charge(self):
        """
        If user don't wanna save a card as payment method - all payment flow
        should be handled at frontend side.
        In other cases, we are applying same flow as for Subscription.
        """

        subscription_service = SubscriptionService(self._client)
        payment = None

        if not self._invoice.is_save_card:
            return payment

        subscription_service.charge(self._invoice)

    def fill_profile(self, user: dict) -> Client:
        serializer = WelcomeCheckoutUserSerializer(self._client, data=user, partial=True)

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
        serializer = WelcomeCheckoutAddressSerializer(data=address)
        serializer.is_valid()

        service = MainAttributeService(self._request.user.client, attribute)
        address = service.create(serializer)

        return address
