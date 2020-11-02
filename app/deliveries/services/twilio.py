from rest_framework import serializers

from core.models import Phone
from core.utils import get_clean_number
from deliveries.models import Request
from deliveries.services.requests import RequestService
from users.choices import Kind
from users.models import Client, Customer


class TwilioFlexService:
    def __init__(self, message: str, phone: str) -> None:
        self._message = message
        self._phone = get_clean_number(phone)

    def create_request(self) -> Request:
        """
        Method, that creates Delivery request when client sent an SMS to our
        number with Twilio Studio.
        """

        self._validate_address()

        address = self._client.main_address

        service = RequestService(client=self._client)

        return service.create(address=address)

    def validate_or_save(self):
        self._validate_or_save_phone()
        self._validate_address()

    @property
    def _client(self) -> Client:
        phone = Phone.objects.get(number=self._phone)
        return phone.client

    def _validate_or_save_phone(self):
        try:
            Phone.objects.get(number=self._phone)
        except Phone.DoesNotExist:
            Customer.objects.get_or_create(phone=self._phone, defaults={"kind": Kind.POSSIBLE,})

            raise serializers.ValidationError(detail="Client not found.", code="client_not_found")

    def _validate_address(self):
        client = self._client

        # if client doesn't have an address
        # we can't handle pickup request
        if not client.main_address:
            raise serializers.ValidationError(
                detail="Client doesn't have an address.", code="no_pickup_address",
            )
