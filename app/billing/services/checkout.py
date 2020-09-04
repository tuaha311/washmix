from django.db.transaction import atomic

from rest_framework.request import Request
from rest_framework.serializers import Serializer
from stripe import PaymentIntent

from api.v1_0.serializers.checkout import CheckoutAddressSerializer, CheckoutUserSerializer
from billing.models import Card, Invoice, Transaction
from core.services.main_attribute import MainAttributeService
from locations.models import Address
from users.models import Client


class CheckoutService:
    def __init__(self, client: Client, request: Request):
        self._client = client
        self._request = request

    def fill_profile(self, user: dict) -> Client:
        serializer = CheckoutUserSerializer(self._client, data=user, partial=True)

        serializer.is_valid()
        serializer.save()

        return self._client

    def create_address(self, address: dict) -> Address:
        serializer = CheckoutAddressSerializer(data=address)
        serializer.is_valid()

        service = MainAttributeService(self._request.user.client, "main_address")
        address = service.create(serializer)

        return address

    def checkout(self, invoice: Invoice, payment: PaymentIntent, card: Card) -> Transaction:
        with atomic():
            transaction = Transaction.objects.create(
                invoice=invoice,
                kind=Transaction.DEBIT,
                provider=Transaction.STRIPE,
                client=self._client,
                stripe_id=payment.id,
                amount=payment.amount,
            )

            invoice.card = card
            invoice.save()

            self._client.subscription = invoice.subscription
            self._client.save()

        return transaction
