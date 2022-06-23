from datetime import date
from unittest.mock import MagicMock, patch

from deliveries.choices import WeekDays
from deliveries.utils import get_dropoff_day


@patch("deliveries.utils.Holiday")
@patch("deliveries.utils.Nonworkingday")
def test_same_week(nonworkingday_class_mock, holiday_class_mock):
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


@patch("deliveries.utils.Holiday")
@patch("deliveries.utils.Nonworkingday")
def test_next_week(nonworkingday_class_mock, holiday_class_mock):
    sat = MagicMock()
    sat.id = 100
    sat.pk = 100
    sat.day = WeekDays.SAT
    sun = MagicMock()
    sun.id = 200
    sun.pk = 200
    sun.day = WeekDays.SUN
    nonworkingday_class_mock.objects.all.return_value = [sat, sun]
    wed_and_rest_of_week = [
        # thu
        [date(2020, 9, 17), date(2020, 9, 21)],
        # fri
        [date(2020, 9, 18), date(2020, 9, 22)],
    ]

    for pickup_date, result in wed_and_rest_of_week:
        assert result == get_dropoff_day(pickup_date)


@patch("deliveries.utils.Holiday")
@patch("deliveries.utils.Nonworkingday")
def test_is_rush(nonworkingday_class_mock, holiday_class_mock):
    mon_tue = [
        # mon
        [date(2020, 9, 14), date(2020, 9, 16)],
        # tue
        [date(2020, 9, 15), date(2020, 9, 17)],
    ]

    for pickup, result in mon_tue:
        actual = get_dropoff_day(pickup, is_rush=True)
        assert result == actual
