from datetime import date

from deliveries.utils import get_dropoff_day


def test_same_week():
    mon_tue = [
        # mon
        [date(2020, 9, 14), date(2020, 9, 17)],
        # tue
        [date(2020, 9, 15), date(2020, 9, 18)],
        # wed
        [date(2020, 9, 16), date(2020, 9, 19)],
    ]

    for pickup, result in mon_tue:
        assert result == get_dropoff_day(pickup)


def test_next_week():
    wed_and_rest_of_week = [
        # thu
        [date(2020, 9, 17), date(2020, 9, 21)],
        # fri
        [date(2020, 9, 18), date(2020, 9, 22)],
    ]

    for pickup_date, result in wed_and_rest_of_week:
        assert result == get_dropoff_day(pickup_date)


def test_is_rush():
    mon_tue = [
        # mon
        [date(2020, 9, 14), date(2020, 9, 16)],
        # tue
        [date(2020, 9, 15), date(2020, 9, 17)],
    ]

    for pickup, result in mon_tue:
        actual = get_dropoff_day(pickup, is_rush=True)
        assert result == actual
