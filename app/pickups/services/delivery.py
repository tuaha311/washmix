from datetime import date, time

from django.conf import settings
from django.utils.timezone import localtime

from rest_framework import serializers

from pickups.models import Delivery
from users.models import Client

SUNDAY_ISO_WEEKDAY = 7
TOTAL_BUSINESS_DAYS = 5


class DeliveryService:
    def __init__(self, client: Client, pickup_date: date, pickup_start: time, pickup_end: time):
        self._client = client
        self._pickup_date = pickup_date
        self._pickup_start = pickup_start
        self._pickup_end = pickup_end

    def create(self) -> Delivery:
        self.validate()

        dropoff_kwargs = self._dropoff_kwargs
        instance = Delivery.objects.create(
            client=self._client,
            pickup_date=self._pickup_date,
            pickup_start=self._pickup_start,
            pickup_end=self._pickup_end,
            **dropoff_kwargs,
        )

        return instance

    def validate(self):
        self._validate_date()
        self._validate_time()
        self._validate_last_call()
        self._validate_common()

    @property
    def _business_days_left(self) -> int:
        business_days_left = TOTAL_BUSINESS_DAYS - self._pickup_date.isoweekday()

        if business_days_left < 0:
            return 0

        return business_days_left

    @property
    def _dropoff_kwargs(self) -> dict:
        """
        Usually, we processing order 2 days and delivering on the next day - i.e.
        3 business days.
        """

        business_days_left = self._business_days_left

        if business_days_left >= settings.ORDER_PROCESSING_BUSINESS_DAYS:
            dropoff_date = self._pickup_date + settings.ORDER_PROCESSING_TIMEDELTA
        else:
            dropoff_date = (
                self._pickup_date
                + settings.ORDER_PROCESSING_TIMEDELTA
                + settings.WEEKENDS_DURATION_TIMEDELTA
            )

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

        # TODO we can't handle pickup date earlier than dropoff date

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
        if now.date() == self._pickup_date and now.time() > settings.TODAY_DELIVERY_LAST_CALL_TIME:
            raise serializers.ValidationError(
                detail="Today last call time is passed - please, choose another day",
                code="today_last_call_is_passed",
            )

    def _validate_common(self):
        if self._pickup_start >= self._pickup_end:
            raise serializers.ValidationError(
                detail="Start time can't be earlier than end.", code="start_earlier_than_end",
            )
