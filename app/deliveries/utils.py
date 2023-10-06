from datetime import date, datetime, time, timedelta
from typing import Tuple

from django.conf import settings
<<<<<<< HEAD
from deliveries.models.categorize_routes import CategorizeRoute
=======
from deliveries.models.delivery import Delivery
>>>>>>> 722ad52 (feat: Introduce Instore Request Feature)

from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Holiday, Nonworkingday


def get_business_days_with_offset(start_date: date, offset: int, dropoff=False, zip_code=None) -> date:
    """
    Common function that handles business days with offset.
    For example, you can use it for calculating the next business day at the end of the week.
    If a categorized route is defined (i.e., zip is provided), the drop-off date will be assigned to the next coming categorized day.
    """
    HOLIDAYS = [i.date.strftime("%Y-%m-%d") for i in Holiday.objects.all()]
    days = [start_date + timedelta(days=index + 1) for index in range(settings.DAYS_IN_YEAR)]
    NON_WORKING_DAYS = []
    pickup_weekday = start_date.isoweekday()
    days_with_deliveries = []
    categorize_route = CategorizeRoute.objects.filter(zip_codes=zip_code).first()

    # Iterate through all CategorizeRoute objects
    for route in CategorizeRoute.objects.filter(zip_codes=zip_code):
        day_number = route.day
        days_with_deliveries.append(day_number)
        
    for obj in Nonworkingday.objects.all():
        NON_WORKING_DAYS.append(int(obj.day))
    
    if not dropoff:
        business_only_days = [
            item
            for item in days
            if item.isoweekday() not in NON_WORKING_DAYS
            and item.strftime("%Y-%m-%d") not in HOLIDAYS
        ]
        if categorize_route and zip_code is not None:
            return find_next_delivery_day(pickup_weekday, days_with_deliveries, start_date)
        else:
            return business_only_days[offset - 1]
    else:
        business_only_days = [
            item
            for item in days
            if item.strftime("%Y-%m-%d") not in HOLIDAYS and item.isoweekday() != 7
        ]
        index = 1
        while (
            business_only_days[offset - index].isoweekday() == 7
            or business_only_days[offset - index].isoweekday() in NON_WORKING_DAYS
        ):
            index -= 1
        if categorize_route and zip_code is not None:
            return find_next_delivery_day(pickup_weekday + 1, days_with_deliveries, start_date + timedelta(days=1))
        else:
            return business_only_days[offset - index]


def get_pickup_day(start_datetime: datetime, client) -> date:
    """
    If the client makes an order before the cutoff time (usually, 9 AM), we can offer
    pickup for today. If the order is made after the cutoff time, it's scheduled for the next business day.

    We don't work on weekends and redirect the pickup date to the first business day of next week (usually, Monday).

    If the zip_code is in a CategorizeRoute, a different logic is applied.
    """
    pickup_time = start_datetime.time()
    pickup_date = start_datetime.date()
    pickup_weekday = pickup_date.isoweekday()
    zip_code = client.main_address.zip_code
    
    categorize_route = CategorizeRoute.objects.filter(zip_codes=zip_code).first()
        
    days_with_deliveries = []

    # Iterate through all CategorizeRoute objects
    for route in CategorizeRoute.objects.filter(zip_codes=zip_code):
        day_number = route.day
        days_with_deliveries.append(day_number)

    HOLIDAYS = [i.date.strftime("%Y-%m-%d") for i in Holiday.objects.all()]
    NON_WORKING_DAYS = []
    for obj in Nonworkingday.objects.all():
        NON_WORKING_DAYS.append(int(obj.day))

    if not categorize_route:

        if pickup_weekday in NON_WORKING_DAYS or pickup_date.strftime("%Y-%m-%d") in HOLIDAYS:
            pickup_date = get_business_days_with_offset(pickup_date, offset=settings.NEXT_DAY)

        elif pickup_time > settings.TODAY_DELIVERY_CUT_OFF_TIME:
            pickup_date = get_business_days_with_offset(pickup_date, offset=settings.NEXT_DAY)

    else:
        if pickup_weekday in NON_WORKING_DAYS or pickup_date.strftime("%Y-%m-%d") in HOLIDAYS:
            pickup_date = find_next_delivery_day(pickup_weekday + 1, days_with_deliveries, pickup_date + timedelta(days=1))
            
        elif pickup_time > settings.TODAY_DELIVERY_CUT_OFF_TIME:
            pickup_date = find_next_delivery_day(pickup_weekday + 1, days_with_deliveries, pickup_date + timedelta(days=1))

        else: 
            pickup_date = find_next_delivery_day(pickup_weekday, days_with_deliveries, pickup_date)
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


def get_dropoff_day(pickup_date: date, is_rush: bool = False, client:object = False) -> date:
    """
    Calculates dropoff date based on pickup date and rush option.
    """

    offset = settings.USUAL_PROCESSING_BUSINESS_DAYS

    if is_rush:
        offset = settings.RUSH_PROCESSING_BUSINESS_DAYS

    return get_business_days_with_offset(pickup_date, offset=offset, dropoff=True, zip_code=client.main_address.zip_code)


def update_deliveries_to_no_show(delivery):
    request = delivery.request
    drop_off_delivery = request.delivery_list.get(kind=DeliveryKind.DROPOFF)
    drop_off_delivery.status = DeliveryStatus.NO_SHOW
    drop_off_delivery.save()
    print("Updated delivery to NO_SHOW: ", drop_off_delivery.pk)

def update_cancelled_deliveries(delivery):
    if delivery.kind == DeliveryKind.DROPOFF:
        request = delivery.request
        pick_up_delivery = request.delivery_list.get(kind=DeliveryKind.PICKUP)
        
        # Check if the corresponding pickup delivery is not cancelled
        if pick_up_delivery.status != DeliveryStatus.CANCELLED:
            # Return an admin notification that pickup cannot be cancelled
            return False
    
    else:
        request = delivery.request
        drop_off_delivery = request.delivery_list.get(kind=DeliveryKind.DROPOFF)
        drop_off_delivery.status = DeliveryStatus.CANCELLED
        drop_off_delivery.save()
        return True

def find_next_delivery_day(pickup_weekday, days_with_deliveries, pickup_date):
    # Sort the available delivery days
    sorted_delivery_days = sorted(map(int, days_with_deliveries))

    for day_number in sorted_delivery_days:
        if day_number > pickup_weekday:
            pickup_date += timedelta(days=(day_number - pickup_weekday))
            return pickup_date

    # If no days in days_with_deliveries are after the pickup_weekday, choose the earliest day
    earliest_day = sorted_delivery_days[0]

    if pickup_weekday <= earliest_day:
        days_to_next_delivery = earliest_day - pickup_weekday
    else:
        # In this case, the earliest available day is after the current pickup_weekday, so we need to wrap around to the next week
        days_to_next_delivery = 7 - (pickup_weekday - earliest_day)

    pickup_date += timedelta(days=days_to_next_delivery)
    
    return pickup_date
    
    
def update_completed_in_store_deliveries(delivery):
    request = delivery.request

    try:
        drop_off_delivery = request.delivery_list.get(kind=DeliveryKind.DROPOFF)
        drop_off_delivery.status = DeliveryStatus.COMPLETED
        drop_off_delivery.save()
        
        return True
    except (Delivery.DoesNotExist, Delivery.MultipleObjectsReturned):
        return False
