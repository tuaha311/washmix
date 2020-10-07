from datetime import datetime, time

from deliveries.utils import get_pickup_start_end


def test_before_working_hours():
    now = datetime(2020, 9, 18, 7, 30)
    assert (time(13, 0), time(15, 0)) == get_pickup_start_end(now)


def test_in_working_hours():

    now = datetime(2020, 9, 18, 11, 30)
    assert (time(15, 30), time(17, 30)) == get_pickup_start_end(now)


def test_start_in_working_hours_and_end_not():
    # TODO проверить еще раз этот кейс
    now = datetime(2020, 9, 18, 13, 30)
    assert (time(17, 30), time(19, 30)) == get_pickup_start_end(now)


def test_after_working_hours():
    now = datetime(2020, 9, 18, 20, 30)
    assert (time(13, 0), time(15, 0)) == get_pickup_start_end(now)
