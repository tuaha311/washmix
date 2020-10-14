from datetime import date, time
from typing import Tuple

from django.conf import settings
from django.utils.timezone import localtime

from rest_framework import serializers

from deliveries.models import Delivery
from deliveries.utils import get_dropoff_day, get_pickup_day, get_pickup_start_end
from users.models import Client


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

        if self._pickup_date.isoweekday() in settings.NON_WORKING_ISO_WEEKENDS:
            raise serializers.ValidationError(
                detail="Pickup day can't be at weekends.", code="cant_pickup_at_weekends",
            )

    def create(self, **extra_kwargs) -> Delivery:
        """
        Like default manager's `create` method but with some changes:
            - Added extra validation on date, time, etc.
            - Added auto completion of dropoff info.
        """

        self.validate()

        dropoff_info = self._dropoff_info
        address = self._client.main_address
        extra_kwargs.setdefault("address", address)

        instance = Delivery.objects.create(
            client=self._client,
            pickup_date=self._pickup_date,
            pickup_start=self._pickup_start,
            pickup_end=self._pickup_end,
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
        self.validate()

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
                **dropoff_info,
                **extra_defaults,
            },
        )

        return instance, created

    def recalculate(self, delivery: Delivery) -> Delivery:
        dropoff_info = self._dropoff_info

        for key, value in dropoff_info.items():
            setattr(delivery, key, value)
        delivery.save()

        return delivery

    def validate(self):
        self._validate_date()
        self._validate_time()
        self._validate_last_call()
        self._validate_common()

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

    def _validate_date(self):
        # we doesn't work at weekends - because we are chilling
        if self._pickup_date.isoweekday() in settings.NON_WORKING_ISO_WEEKENDS:
            raise serializers.ValidationError(
                detail="Delivery doesn't work at weekends.", code="pickup_date_is_weekends",
            )

        # we can't handle pickup date which is passed (in past)
        now = localtime()
        if now.date() > self._pickup_date:
            raise serializers.ValidationError(
                detail="Delivery can't handle passed date.", code="pickup_date_is_passed",
            )

    def _validate_time(self):
        # we can't pickup earlier than we start working
        if self._pickup_start < settings.DELIVERY_START_WORKING:
            raise serializers.ValidationError(
                detail="Start time can't be earlier than our work time.",
                code="start_earlier_than_our_working_hours",
            )

        # we can't pickup after than we finish working
        if self._pickup_end > settings.DELIVERY_END_WORKING:
            raise serializers.ValidationError(
                detail="End time can't be later than our work time.",
                code="end_later_than_our_working_hours",
            )

    def _validate_last_call(self):
        # we can't handle today pickup if it was made after last call
        now = localtime()
        today = now.date()

        if today == self._pickup_date and now.time() > settings.TODAY_DELIVERY_CUT_OFF_TIME:
            raise serializers.ValidationError(
                detail="Today last call time is passed - please, choose another day",
                code="today_last_call_is_passed",
            )

    def _validate_common(self):
        if self._pickup_start >= self._pickup_end:
            raise serializers.ValidationError(
                detail="Start time can't be earlier than end.", code="start_earlier_than_end",
            )
