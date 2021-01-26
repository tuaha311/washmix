from datetime import datetime, time

from deliveries.utils import get_pickup_start_end


def test_before_working_hours():
    now = datetime(2020, 9, 18, 7, 30)
    assert (time(13, 0), time(15, 0)) == get_pickup_start_end(now)


def test_in_working_hours():
    now = datetime(2020, 9, 18, 11, 30)
    assert (time(15, 30), time(17, 30)) == get_pickup_start_end(now)


def test_after_working_hours_2():
    now = datetime(2020, 9, 17, 20, 30)
    assert (time(13, 0), time(15, 0)) == get_pickup_start_end(now)


def test_start_in_working_hours_and_end_not():
    now = datetime(2020, 9, 18, 13, 30)
    assert (time(13, 0), time(15, 0)) == get_pickup_start_end(now)


def test_after_working_hours():
    now = datetime(2020, 9, 18, 20, 30)
    assert (time(13, 0), time(15, 0)) == get_pickup_start_end(now)


def test_different_time():
    pickup_start_list = [
        [datetime(2021, 1, 26, 0, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 1, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 2, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 3, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 4, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 5, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 6, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 7, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 8, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 9, 30), (time(13, 30), time(15, 30))],
        [datetime(2021, 1, 26, 10, 30), (time(14, 30), time(16, 30))],
        [datetime(2021, 1, 26, 11, 30), (time(15, 30), time(17, 30))],
        [datetime(2021, 1, 26, 12, 30), (time(16, 30), time(18, 30))],
        [datetime(2021, 1, 26, 13, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 14, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 15, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 16, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 17, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 18, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 19, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 20, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 21, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 22, 30), (time(13, 0), time(15, 0))],
        [datetime(2021, 1, 26, 23, 30), (time(13, 0), time(15, 0))],
    ]

    for pickup_start, result in pickup_start_list:
        possible_result = get_pickup_start_end(pickup_start)
        assert result == possible_result
