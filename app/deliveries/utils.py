from datetime import date, datetime, time, timedelta
from typing import Tuple

from django.conf import settings


def get_business_days_with_offset(start_date: date, offset: int) -> date:
    """
    Common function, that handles business days with offset.
    For example, you can use it for calculating next business day at end of week.
    """

    days = [start_date + timedelta(days=index + 1) for index in range(settings.DAYS_IN_YEAR)]
    business_only_days = [
        item for item in days if item.isoweekday() not in settings.NON_WORKING_ISO_WEEKENDS
    ]

    return business_only_days[offset - 1]


def get_pickup_day(start_datetime: datetime) -> date:
    """
    If client make order before cut off time (usually, 9AM) - we can offer
    to him pickup for today.
    If he made order after cut off time - to the next business day.

    We doesn't working in weekends and redirect pickup date to the first business
    day of next week (usually, Monday).
    """

    pickup_time = start_datetime.time()
    pickup_date = start_datetime.date()
    pickup_weekday = pickup_date.isoweekday()

    if pickup_weekday in settings.NON_WORKING_ISO_WEEKENDS:
        pickup_date = get_business_days_with_offset(pickup_date, offset=settings.NEXT_DAY)

    elif pickup_time > settings.TODAY_DELIVERY_CUT_OFF_TIME:
        pickup_date = get_business_days_with_offset(pickup_date, offset=settings.NEXT_DAY)

    return pickup_date


def get_pickup_start_end(start_datetime: datetime) -> Tuple[time, time]:
    """
    This function tries to find most closes time of pickup.
    For example - if we received client request pickup at 3AM, obviously,
    we can't rush to him for now. And in this case we are waiting for today
    opening hours.
    """

    # we can't pickup right now, we will came in 4 hours after your pickup request
    pickup_start_datetime = start_datetime + settings.PICKUP_SAME_DAY_START_TIMEDELTA
    pickup_start_time = pickup_start_datetime.time()
    # we are giving to client time gap in 2 hours
    pickup_end_datetime = pickup_start_datetime + settings.PICKUP_SAME_DAY_END_TIMEDELTA
    pickup_end_time = pickup_end_datetime.time()

    if not (
        settings.DELIVERY_END_WORKING > pickup_start_time > settings.DELIVERY_START_WORKING
    ) or not (settings.DELIVERY_END_WORKING > pickup_end_time > settings.DELIVERY_START_WORKING):
        pickup_start_datetime = datetime(
            year=start_datetime.year,
            month=start_datetime.month,
            day=start_datetime.day,
            hour=settings.DELIVERY_START_WORKING.hour,
            minute=settings.DELIVERY_START_WORKING.minute,
        )
        pickup_end_datetime = pickup_start_datetime + settings.PICKUP_SAME_DAY_END_TIMEDELTA

    return pickup_start_datetime.time(), pickup_end_datetime.time()


def get_dropoff_day(pickup_date: date, is_rush: bool = False) -> date:
    """
    Calculates dropoff date based on pickup date and rush option.
    """

    offset = settings.USUAL_PROCESSING_BUSINESS_DAYS

    if is_rush:
        offset = settings.RUSH_PROCESSING_BUSINESS_DAYS

    return get_business_days_with_offset(pickup_date, offset=offset)
