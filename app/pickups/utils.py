from datetime import date, timedelta

from django.conf import settings


def get_next_business_day(today: date):
    today_weekday = today.isoweekday()
    probable_day = today + timedelta(days=1)
    probable_weekday = probable_day.isoweekday()

    if probable_weekday in settings.NON_WORKING_ISO_WEEKENDS:
        delta_weekdays = settings.FULL_WEEK_LENGTH - today_weekday
        probable_day = probable_day + timedelta(days=delta_weekdays)

    return probable_day
