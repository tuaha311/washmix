from typing import List, Optional

from django.db.transaction import atomic

from rest_framework.request import Request
from stripe import PaymentMethod
from stripe.error import StripeError

from billing.models import Card, Invoice, Transaction
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

    def charge(self) -> Optional[PaymentMethod]:
        # card will be charged at the frontend side
        # if user doesn't want to save a card
        if not self._invoice.is_save_card:
            return None

        payment = None

        for item in self._client.card_list.all():
            # we are trying to charge the card list of client
            # and we are stopping at first successful attempt
            try:
                payment = self._stripe_helper.create_payment_intent(
                    payment_method_id=item.stripe_id,
                    amount=self._invoice.amount,
                    invoice=self._invoice,
                )

                self._client.main_card = item
                self._client.save()

                # we are exiting from the cycle at first successful attempt
                break

            except StripeError:
                continue

        return payment

    def checkout(self, payment: PaymentMethod) -> Optional[Transaction]:
        # .checkout method works idempotently - if we already marked
        # invoice as paid, than we doesn't make changes
        if self._invoice.is_paid:
            return None

        with atomic():
            transaction = Transaction.objects.create(
                invoice=self._invoice,
                kind=Transaction.DEBIT,
                provider=Transaction.STRIPE,
                client=self._client,
                stripe_id=payment.id,
                amount=payment.amount,
                source=payment,
            )

            # don't save a card if it wasn't marked by user
            if not self._invoice.is_save_card:
                self._invoice.card = self._client.main_card
                self._invoice.save()

            self._client.subscription = self._invoice.subscription
            self._client.save()

        return transaction

    def _create_address(self, address: dict, attribute: str):
        serializer = CheckoutAddressSerializer(data=address)
        serializer.is_valid()

        service = MainAttributeService(self._request.user.client, attribute)
        address = service.create(serializer)

        return address
