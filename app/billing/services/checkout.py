from typing import List

from django.db.transaction import atomic

from rest_framework.request import Request
from stripe import PaymentMethod
from stripe.error import StripeError

from api.v1_0.serializers.checkout import CheckoutAddressSerializer, CheckoutUserSerializer
from billing.models import Card, Invoice, Transaction
from billing.stripe_helper import StripeHelper
from core.services.main_attribute import MainAttributeService
from locations.models import Address
from users.models import Client


class CheckoutService:
    def __init__(self, client: Client, request: Request):
        self._client = client
        self._request = request
        self._stripe_helper = StripeHelper(client)

    def save_card_list(self) -> List[Card]:
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

    def create_address(self, address: dict) -> Address:
        serializer = CheckoutAddressSerializer(data=address)
        serializer.is_valid()

        service = MainAttributeService(self._request.user.client, "main_address")
        address = service.create(serializer)

        return address

    def charge(self, invoice: Invoice) -> PaymentMethod:
        payment = None

        for item in self._client.card_list.all():
            # we are trying to charge the card list of client
            try:
                payment = self._stripe_helper.create_payment_intent(
                    payment_method_id=item.stripe_id, amount=invoice.amount,
                )

                self._client.main_card = item
                self._client.save()

                # we are exiting at first successful attempt
                return payment

            except StripeError:
                continue

        if not payment:
            raise InterruptedError

    def checkout(self, invoice: Invoice, payment: PaymentMethod) -> Transaction:
        with atomic():
            transaction = Transaction.objects.create(
                invoice=invoice,
                kind=Transaction.DEBIT,
                provider=Transaction.STRIPE,
                client=self._client,
                stripe_id=payment.id,
                amount=payment.amount,
            )

            invoice.card = self._client.main_card
            invoice.save()

            self._client.subscription = invoice.subscription
            self._client.save()

        return transaction
