import time
import pickle
import calendar
from datetime import datetime, timedelta

import mock
import pytest
from dateutil import tz

import pytool


def test_utc_singleton():
    assert pytool.time.UTC() == pytool.time.UTC()


def test_utc_methods():
    assert pytool.time.UTC().utcoffset(datetime.now()) == timedelta(0)
    assert pytool.time.UTC().tzname(datetime.now()) == "UTC"
    assert pytool.time.UTC().dst(datetime.now()) == timedelta(0)


def test_utc_pickle():
    pickled = pickle.dumps(pytool.time.UTC())
    utc = pickle.loads(pickled)
    assert utc == pytool.time.UTC()


@mock.patch("datetime.datetime")
def test_utcnow(datetime):
    pytool.time.utcnow()
    datetime.now.assert_called_with(pytool.time.UTC())


def test_utc_makes_tzaware_utc_datetime():
    stamp = pytool.time.utc(2023, 12, 1)
    assert stamp.tzinfo == pytool.time.UTC()
    assert stamp == datetime(2023, 12, 1, tzinfo=pytool.time.UTC())
    expected = pytool.time.as_utc(
        datetime(2023, 11, 30, 16, 0, tzinfo=tz.gettz("America/Los_Angeles"))
    )
    assert stamp == expected


def test_trim_time():
    now = datetime.now()
    stamp = pytool.time.trim_time(now)
    assert stamp.year == now.year
    assert stamp.month == now.month
    assert stamp.day == now.day
    assert stamp.hour == 0
    assert stamp.minute == 0
    assert stamp.second == 0
    assert stamp.tzinfo == now.tzinfo


def test_trim_time_utc():
    now = pytool.time.utcnow()
    stamp = pytool.time.trim_time(now)

    assert stamp.year == now.year
    assert stamp.month == now.month
    assert stamp.day == now.day
    assert stamp.hour == 0
    assert stamp.minute == 0
    assert stamp.second == 0
    assert stamp.tzinfo == now.tzinfo


def test_fromutctimestamp_summer():
    d = datetime(2012, 6, 1, tzinfo=pytool.time.UTC())
    stamp = calendar.timegm(d.utctimetuple())
    assert pytool.time.fromutctimestamp(stamp) == d


def test_fromutctimestamp_winter():
    d = datetime(2012, 1, 1, tzinfo=pytool.time.UTC())
    stamp = calendar.timegm(d.utctimetuple())
    assert pytool.time.fromutctimestamp(stamp) == d


def test_fromutctimestamp_now():
    d = pytool.time.utcnow()
    stamp = calendar.timegm(d.utctimetuple()) + (1.0 * d.microsecond / 10**6)
    assert pytool.time.fromutctimestamp(stamp) == d


def test_toutctimestamp():
    d = datetime.now()
    u = pytool.time.utcnow()
    decimal = 1.0 * d.microsecond / 10**6
    assert pytool.time.toutctimestamp(d) == (
        calendar.timegm(u.utctimetuple()) + decimal
    )


def test_toutctimestamp_utctz():
    d = pytool.time.utcnow()
    decimal = 1.0 * d.microsecond / 10**6
    assert pytool.time.toutctimestamp(d) == (
        calendar.timegm(d.utctimetuple()) + decimal
    )


def test_toutctimestamp_summer():
    d = datetime(2012, 6, 1, tzinfo=pytool.time.UTC())
    s = pytool.time.toutctimestamp(d)
    assert d.timetuple() == pytool.time.fromutctimestamp(s).timetuple()


def test_toutctimestamp_winter():
    d = datetime(2012, 1, 1, tzinfo=pytool.time.UTC())
    s = pytool.time.toutctimestamp(d)
    assert d.timetuple() == pytool.time.fromutctimestamp(s).timetuple()


def test_toutctimestamp_close_enough():
    t = int(time.time())
    d = int(pytool.time.toutctimestamp(datetime.now()))
    assert t == d


def test_toutctimestamp_close_enough_tzaware():
    t = int(time.time())
    d = int(pytool.time.toutctimestamp(pytool.time.utcnow()))
    assert t == d


def test_as_utc():
    d = pytool.time.utcnow()
    assert d == pytool.time.as_utc(d)


def test_as_utc_multi():
    t = pytool.time.utcnow()
    d = pytool.time.as_utc(t)
    assert d == pytool.time.as_utc(t)
    d = pytool.time.as_utc(d)
    assert d == pytool.time.as_utc(t)
    d = pytool.time.as_utc(d)
    assert d == pytool.time.as_utc(t)


def test_as_utc_naive():
    d = datetime.now()
    d2 = d + timedelta(seconds=time.altzone if pytool.time.is_dst(d) else time.timezone)
    d = pytool.time.as_utc(d)
    # Can't compare naive and aware datetimes, so we do it manually
    for field in ("year", "month", "day", "hour", "minute", "second", "microsecond"):
        assert getattr(d, field) == getattr(d2, field)


# These daylight savings tests are a bit sloppy, but oh well
@pytest.mark.skipif(
    "UTC" in time.tzname, reason="Test doesn't work if server timezone is UTC"
)
def test_is_dst():
    d = datetime(2000, 6, 1)
    assert pytool.time.is_dst(d) is True


@pytest.mark.skipif(
    "UTC" in time.tzname, reason="Test doesn't work if server timezone is UTC"
)
def test_is_not_dst():
    d = datetime(2000, 11, 30)
    assert pytool.time.is_dst(d) is False


def test_week_start():
    start = pytool.time.week_start(datetime.now())
    assert start.weekday() == 0
    assert start.hour == 0
    assert start.minute == 0
    assert start.second == 0
    assert start.microsecond == 0


def test_week_seconds_start():
    secs = pytool.time.week_seconds(pytool.time.week_start(datetime.now()))
    assert secs == 0


def test_week_seconds():
    start = pytool.time.week_start(datetime.now())
    for i in range(7):
        assert (
            pytool.time.week_seconds(start + timedelta(days=i))
            == timedelta(days=i).total_seconds()
        )


def test_week_seconds_to_datetime():
    for i in range(7):
        assert pytool.time.week_start(datetime.now()) + timedelta(
            days=i
        ) == pytool.time.week_seconds_to_datetime(timedelta(days=i).total_seconds())


def test_make_week_seconds():
    assert pytool.time.make_week_seconds(0, 1) == 60 * 60
    assert pytool.time.make_week_seconds(1, 0) == 60 * 60 * 24
    assert pytool.time.make_week_seconds(7, 0) == 0
    assert (
        pytool.time.make_week_seconds(2, 1, 1, 1) == 60 * 60 * 24 * 2 + 60 * 60 + 60 + 1
    )


def test_floor_minute():
    stamp = pytool.time.utcnow()
    assert pytool.time.floor_minute(stamp) == datetime(
        stamp.year,
        stamp.month,
        stamp.day,
        stamp.hour,
        stamp.minute,
        tzinfo=stamp.tzinfo,
    )


def test_floor_day():
    stamp = pytool.time.utcnow()
    assert pytool.time.floor_day(stamp) == datetime(
        *stamp.date().timetuple()[:-3], tzinfo=pytool.time.UTC()
    )


def test_floor_week():
    stamp = pytool.time.utcnow()
    start = stamp - timedelta(days=stamp.weekday())
    assert pytool.time.floor_week(stamp) == datetime(
        start.year, start.month, start.day, tzinfo=pytool.time.UTC()
    )


def test_floor_month():
    stamp = pytool.time.utcnow()
    assert pytool.time.floor_month(stamp) == datetime(
        *(stamp.date().timetuple()[:2] + (1,)), tzinfo=pytool.time.UTC()
    )


def test_timer_init_works():
    pytool.time.Timer()


def test_timer_elapsed_works():
    with mock.patch("pytool.time.utcnow") as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 0, 0)
        t = pytool.time.Timer()
    with mock.patch("pytool.time.utcnow") as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 1, 0)
        assert t.elapsed == timedelta(seconds=60)
    with mock.patch("pytool.time.utcnow") as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 1, 0, 0)
        assert t.elapsed == timedelta(seconds=60 * 60)


def test_timer_mark_works():
    with mock.patch("pytool.time.utcnow") as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 0, 0)
        t = pytool.time.Timer()
    with mock.patch("pytool.time.utcnow") as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 1, 0)
        assert t.mark() == timedelta(seconds=60)
    with mock.patch("pytool.time.utcnow") as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 3, 0)
        assert t.mark() == timedelta(seconds=2 * 60)


def test_ago_regular():
    unix = 14386000000
    stamp = pytool.time.fromutctimestamp(unix)
    # Previous stamp minus 1 day, 1 hour, 1 minute and 1 second
    ago = unix - (24 * 60 * 60) - (60 * 60) - 60 - 1
    ago = pytool.time.fromutctimestamp(ago)

    assert pytool.time.ago(stamp, days=1, hours=1, minutes=1, seconds=1) == ago


def test_ago_shorter():
    unix = 14386000000
    stamp = pytool.time.fromutctimestamp(unix)
    # Previous stamp minus 1 day, 1 hour, 1 minute and 1 second
    ago = unix - (24 * 60 * 60) - (60 * 60) - 60 - 1
    ago = pytool.time.fromutctimestamp(ago)

    assert pytool.time.ago(stamp, days=1, hrs=1, mins=1, secs=1) == ago


def test_ago_shorthand():
    unix = 14386000000
    stamp = pytool.time.fromutctimestamp(unix)
    # Previous stamp minus 1 day, 1 hour, 1 minute and 1 second
    ago = unix - (24 * 60 * 60) - (60 * 60) - 60 - 1
    ago = pytool.time.fromutctimestamp(ago)

    assert pytool.time.ago(stamp, d=1, h=1, m=1, s=1) == ago
