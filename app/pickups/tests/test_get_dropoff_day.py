from datetime import date

from pickups.utils import get_dropoff_day


def test_same_week():
    mon_tue = [
        # mon
        [date(2020, 9, 14), date(2020, 9, 17)],
        # tue
        [date(2020, 9, 15), date(2020, 9, 18)],
    ]

    for pickup, result in mon_tue:
        assert result == get_dropoff_day(pickup)


def test_next_week():
    wed_and_rest_of_week = [
        # wed
        [date(2020, 9, 16), date(2020, 9, 21)],
        # thu
        [date(2020, 9, 17), date(2020, 9, 22)],
        # fri
        [date(2020, 9, 18), date(2020, 9, 23)],
    ]

    for pickup_date, result in wed_and_rest_of_week:
        assert result == get_dropoff_day(pickup_date)
