from datetime import date, time

from django.conf import settings
from django.utils.timezone import localtime

from rest_framework import serializers

from deliveries.models import Holiday, Nonworkingday


class RequestValidator:
    def __init__(
        self,
        pickup_date: date,
        pickup_start: time,
        pickup_end: time,
    ):
        self._pickup_date = pickup_date
        self._pickup_start = pickup_start
        self._pickup_end = pickup_end

        HOLIDAYS = [
            "%02d-%02d-%02d" % (i.date.year, i.date.month, i.date.day)
            for i in Holiday.objects.all()
        ]
        NON_WORKING_DAYS = []
        for obj in Nonworkingday.objects.all():
            NON_WORKING_DAYS.append(int(obj.day))

        print(self._pickup_date)
        if self._pickup_date.isoweekday() in NON_WORKING_DAYS:
            raise serializers.ValidationError(
                detail="Pickup day can't be at weekends",
                code="cant_pickup_at_weekends",
            )
        elif str(self._pickup_date) in HOLIDAYS:
            raise serializers.ValidationError(
                detail="Pickup day can't be at holidays",
                code="cant_pickup_at_weekends",
            )

        # if self._pickup_date.isoweekday() in settings.NON_WORKING_DAYS:
        #     raise serializers.ValidationError(
        #         detail="Pickup day can't be at weekends.",
        #         code="cant_pickup_at_weekends",
        #     )

    def validate(self):
        self._validate_date()
        self._validate_time()
        self._validate_last_call()
        self._validate_common()

    def _validate_date(self):
        # we doesn't work at weekends - because we are chilling

        HOLIDAYS = [
            "%02d-%02d-%02d" % (i.date.year, i.date.month, i.date.day)
            for i in Holiday.objects.all()
        ]
        NON_WORKING_DAYS = []
        for obj in Nonworkingday.objects.all():
            NON_WORKING_DAYS.append(int(obj.day))

        if self._pickup_date.isoweekday() in NON_WORKING_DAYS:
            raise serializers.ValidationError(
                detail="Pickup day can't be at weekends.",
                code="cant_pickup_at_weekends",
            )
        elif str(self._pickup_date) in HOLIDAYS:
            raise serializers.ValidationError(
                detail="Pickup day can't be at holidays",
                code="cant_pickup_at_weekends",
            )

        # if self._pickup_date.isoweekday() in settings.NON_WORKING_DAYS:
        #     raise serializers.ValidationError(
        #         detail="Delivery doesn't work at weekends.",
        #         code="pickup_date_is_weekends",
        #     )

        # we can't handle pickup date which is passed (in past)
        now = localtime()
        if now.date() > self._pickup_date:
            raise serializers.ValidationError(
                detail="Delivery can't handle passed date.",
                code="pickup_date_is_passed",
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
                detail="Start time can't be earlier than end.",
                code="start_earlier_than_end",
            )
