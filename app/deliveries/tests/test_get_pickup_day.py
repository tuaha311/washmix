from datetime import date, datetime
from unittest.mock import patch

from deliveries.utils import get_pickup_day


def test_same_day():
    dates = [
        [datetime(2020, 9, 14, 7, 30), date(2020, 9, 14)],
        [datetime(2020, 9, 14, 4, 00), date(2020, 9, 14)],
    ]

    for start, result in dates:
        assert start, result == get_pickup_day(start)


def test_next_day():
    dates = [
        [datetime(2020, 9, 14, 14, 30), date(2020, 9, 15)],
        [datetime(2020, 9, 14, 23, 30), date(2020, 9, 15)],
    ]

    for start, result in dates:
        assert start, result == get_pickup_day(start)


@patch("deliveries.utils.Holiday")
@patch("deliveries.utils.Nonworkingday")
def test_friday_and_weekends(nonworkingday_class_mock, holiday_class_mock):
    fri_and_weekends = [
        # fri, same day and next
        [datetime(2020, 9, 18, 7, 30), date(2020, 9, 18)],
        [datetime(2020, 9, 18, 14, 30), date(2020, 9, 19)],
        # sat, same day and next
        [datetime(2020, 9, 19, 7, 30), date(2020, 9, 19)],
        [datetime(2020, 9, 19, 14, 30), date(2020, 9, 21)],
        # sun, same day and next
        [datetime(2020, 9, 20, 7, 30), date(2020, 9, 21)],
        [datetime(2020, 9, 20, 14, 30), date(2020, 9, 21)],
    ]

    for start, result in fri_and_weekends:
        assert result == get_pickup_day(start)
