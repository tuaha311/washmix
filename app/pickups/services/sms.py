from django.utils.timezone import localtime

from rest_framework import serializers

from core.models import Phone
from pickups.models import Delivery
from pickups.services.delivery import DeliveryService
from users.models import Client, Customer


class TwilioFlexService:
    def __init__(self, message: str, phone: str) -> None:
        self._message = message
        self._phone = phone

    def create_delivery(self) -> Delivery:
        self._validate_address()

        pickup_kwargs = self._pickup_kwargs
        service = DeliveryService(client=self._client, **pickup_kwargs,)
        delivery = service.create()

        return delivery

    def validate(self):
        self._validate_or_save_phone()
        self._validate_address()

    @property
    def _pickup_kwargs(self) -> dict:
        now = localtime()
        return {}

    @property
    def _client(self) -> Client:
        phone = Phone.objects.get(number=self._phone)
        return phone.client

    def _validate_or_save_phone(self):
        try:
            Phone.objects.get(number=self._phone)
        except Phone.DoesNotExist:
            Customer.objects.get_or_create(phone=self._phone, defaults={"kind": Customer.POSSIBLE,})

            raise serializers.ValidationError(detail="Client not found.", code="client_not_found")

    def _validate_address(self):
        client = self._client

        # if client doesn't have an address
        # we can't handle pickup request
        if not client.main_address:
            raise serializers.ValidationError(
                detail="Client doesn't have an address.", code="no_pickup_address",
            )
