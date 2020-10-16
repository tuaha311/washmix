from datetime import date, time
from typing import Tuple

from django.conf import settings
from django.utils.timezone import localtime

from deliveries.models import Delivery
from deliveries.utils import get_dropoff_day, get_pickup_day, get_pickup_start_end
from deliveries.validators import DeliveryValidator
from users.models import Client

DEFAULT_AMOUNT = 0


class DeliveryService:
    def __init__(
        self,
        client: Client,
        pickup_date: date = None,
        pickup_start: time = None,
        pickup_end: time = None,
    ):
        self._client = client

        if pickup_date is None:
            pickup_date = self._pickup_day_auto_complete

        if pickup_start is None or pickup_end is None:
            pickup_start, pickup_end = self._pickup_start_end_auto_complete

        self._pickup_date = pickup_date
        self._pickup_start = pickup_start
        self._pickup_end = pickup_end
        self._validator_service = DeliveryValidator(pickup_date, pickup_start, pickup_end)

    def create(self, **extra_kwargs) -> Delivery:
        """
        Like default manager's `create` method but with some changes:
            - Added extra validation on date, time, etc.
            - Added auto completion of dropoff info.
        """

        self._validator_service.validate()

        dropoff_info = self._dropoff_info
        address = self._client.main_address
        extra_kwargs.setdefault("address", address)

        instance = Delivery.objects.create(
            client=self._client,
            pickup_date=self._pickup_date,
            pickup_start=self._pickup_start,
            pickup_end=self._pickup_end,
            amount=DEFAULT_AMOUNT,
            **dropoff_info,
            **extra_kwargs,
        )

        return instance

    def get_or_create(self, extra_query: dict, extra_defaults: dict) -> Tuple[Delivery, bool]:
        """
        Like default manager's `get_or_create` method but with some changes:
            - Added extra validation on date, time, etc.
            - Added auto completion of dropoff info.
        """

        self._validator_service.validate()

        dropoff_info = self._dropoff_info
        address = self._client.main_address
        extra_query.setdefault("address", address)

        instance, created = Delivery.objects.get_or_create(
            client=self._client,
            **extra_query,
            defaults={
                "pickup_date": self._pickup_date,
                "pickup_start": self._pickup_start,
                "pickup_end": self._pickup_end,
                "amount": DEFAULT_AMOUNT,
                **dropoff_info,
                **extra_defaults,
            },
        )

        return instance, created

    def recalculate(self, delivery: Delivery) -> Delivery:
        """
        This method helps to recalculate dropoff info on update
        field `pickup_date`.
        """

        dropoff_info = self._dropoff_info

        for key, value in dropoff_info.items():
            setattr(delivery, key, value)
        delivery.save()

        return delivery

    def validate(self):
        self._validator_service.validate()

    @property
    def _pickup_start_end_auto_complete(self) -> Tuple[time, time]:
        now = localtime()
        return get_pickup_start_end(now)

    @property
    def _pickup_day_auto_complete(self) -> date:
        now = localtime()
        return get_pickup_day(now)

    @property
    def _dropoff_info(self) -> dict:
        """
        Usually, we processing order 2 days and delivering on the next day - i.e.
        3 business days.
        """

        dropoff_date = get_dropoff_day(self._pickup_date)

        return {
            "dropoff_date": dropoff_date,
            "dropoff_start": self._pickup_start,
            "dropoff_end": self._pickup_end,
        }
