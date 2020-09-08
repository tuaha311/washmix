from datetime import date, time

from django.conf import settings
from django.utils.timezone import localtime

from rest_framework import serializers

SUNDAY_WEEKDAY = 6


class DeliveryService:
    def __init__(self, pickup_date: date, pickup_start: time, pickup_end: time):
        self._pickup_date = pickup_date
        self._pickup_start = pickup_start
        self._pickup_end = pickup_end

    def calculate_dropoff(self) -> dict:
        """
        Usually, we processing order 2 days and delivering on the next day - i.e.
        3 business days.
        """

        dropoff_date = self._pickup_date + settings.ORDER_PROCESSING_BUSINESS_DAYS

        return {
            "dropoff_date": dropoff_date,
            "dropoff_start": self._pickup_start,
            "dropoff_end": self._pickup_end,
        }

    def validate_date(self):
        # we doesn't work at weekends - because we are chilling
        if self._pickup_date.weekday() in settings.NON_WORKING_WEEKENDS:
            raise serializers.ValidationError(
                detail="Delivery doesn't work at weekends.", code="pickup_date_is_weekends",
            )

        # we can't handle pickup date which is passed (in past)
        now = localtime()
        if now.date() > self._pickup_date:
            raise serializers.ValidationError(
                detail="Delivery can't handle passed date.", code="pickup_date_is_passed",
            )

    def validate_time(self):
        # we can't pickup earlier than we start working
        if self._pickup_start < settings.DELIVERY_START_WORKING:
            raise serializers.ValidationError(
                detail="Start time can't be earlier than our work time.",
                code="start_earlier_than_our_working_hours",
            )

        if self._pickup_end > settings.DELIVERY_END_WORKING:
            raise serializers.ValidationError(
                detail="End time can't be later than our work time.",
                code="end_later_than_our_working_hours",
            )

    def validate_last_call(self):
        # we can't handle today pickup if it was made after last call
        now = localtime()
        if now.date() == self._pickup_date and now.time() > settings.TODAY_DELIVERY_LAST_CALL_TIME:
            raise serializers.ValidationError(
                detail="Today last call time is passed - please, choose another day",
                code="today_last_call_is_passed",
            )

    def validate(self):
        if self._pickup_start >= self._pickup_end:
            raise serializers.ValidationError(
                detail="Start time can't be earlier than end.", code="start_earlier_than_end",
            )
