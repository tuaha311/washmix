from datetime import date, time

from django.conf import settings
from django.utils.timezone import localtime

from rest_framework import serializers

from locations.models import Address
from pickups.utils import get_dropoff_day
from users.models import Client


class DeliveryService:
    def __init__(
        self,
        client: Client,
        address: Address,
        pickup_date: date,
        pickup_start: time,
        pickup_end: time,
    ):
        self._client = client
        self._address = address
        self._pickup_date = pickup_date
        self._pickup_start = pickup_start
        self._pickup_end = pickup_end

        assert (
            self._pickup_date.isoweekday() not in settings.NON_WORKING_ISO_WEEKENDS
        ), "We doesn't working at weekends."

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
