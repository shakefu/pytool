import time
import calendar
from datetime import datetime, timedelta

import mock
from nose import SkipTest

import pytool
from .util import eq_


def test_utc_singleton():
    eq_(pytool.time.UTC(), pytool.time.UTC())


def test_utc_methods():
    eq_(pytool.time.UTC().utcoffset(datetime.now()), timedelta(0))
    eq_(pytool.time.UTC().tzname(datetime.now()), 'UTC')
    eq_(pytool.time.UTC().dst(datetime.now()), timedelta(0))


@mock.patch('datetime.datetime')
def test_utcnow(datetime):
    pytool.time.utcnow()
    datetime.now.assert_called_with(pytool.time.UTC())


def test_trim_time():
    now = datetime.now()
    stamp = pytool.time.trim_time(now)

    eq_(stamp.year, now.year)
    eq_(stamp.month, now.month)
    eq_(stamp.day, now.day)
    eq_(stamp.hour, 0)
    eq_(stamp.minute, 0)
    eq_(stamp.second, 0)
    eq_(stamp.tzinfo, now.tzinfo)


def test_trim_time_utc():
    now = pytool.time.utcnow()
    stamp = pytool.time.trim_time(now)

    eq_(stamp.year, now.year)
    eq_(stamp.month, now.month)
    eq_(stamp.day, now.day)
    eq_(stamp.hour, 0)
    eq_(stamp.minute, 0)
    eq_(stamp.second, 0)
    eq_(stamp.tzinfo, now.tzinfo)


def test_fromutctimestamp_summer():
    d = datetime(2012, 6, 1, tzinfo=pytool.time.UTC())
    stamp = calendar.timegm(d.utctimetuple())
    eq_(pytool.time.fromutctimestamp(stamp), d)


def test_fromutctimestamp_winter():
    d = datetime(2012, 1, 1, tzinfo=pytool.time.UTC())
    stamp = calendar.timegm(d.utctimetuple())
    eq_(pytool.time.fromutctimestamp(stamp), d)


def test_fromutctimestamp_now():
    d = pytool.time.utcnow()
    stamp = calendar.timegm(d.utctimetuple()) + (1.0 * d.microsecond / 10**6)
    eq_(pytool.time.fromutctimestamp(stamp), d)


def test_toutctimestamp():
    d = datetime.now()
    u = pytool.time.utcnow()
    decimal = (1.0 * d.microsecond / 10**6)
    eq_(pytool.time.toutctimestamp(d), calendar.timegm(u.utctimetuple()) + decimal)


def test_toutctimestamp_utctz():
    d = pytool.time.utcnow()
    decimal = (1.0 * d.microsecond / 10**6)
    eq_(pytool.time.toutctimestamp(d), calendar.timegm(d.utctimetuple()) + decimal)


def test_toutctimestamp_summer():
    d = datetime(2012, 6, 1, tzinfo=pytool.time.UTC())
    s = pytool.time.toutctimestamp(d)
    eq_(d.timetuple(), pytool.time.fromutctimestamp(s).timetuple())


def test_toutctimestamp_winter():
    d = datetime(2012, 1, 1, tzinfo=pytool.time.UTC())
    s = pytool.time.toutctimestamp(d)
    eq_(d.timetuple(), pytool.time.fromutctimestamp(s).timetuple())


def test_toutctimestamp_close_enough():
    t = int(time.time())
    d = int(pytool.time.toutctimestamp(datetime.now()))
    eq_(t, d)


def test_toutctimestamp_close_enough_tzaware():
    t = int(time.time())
    d = int(pytool.time.toutctimestamp(pytool.time.utcnow()))
    eq_(t, d)


def test_as_utc():
    d = pytool.time.utcnow()
    eq_(d, pytool.time.as_utc(d))


def test_as_utc_multi():
    t = pytool.time.utcnow()
    d = pytool.time.as_utc(t)
    eq_(d, pytool.time.as_utc(t))
    d = pytool.time.as_utc(d)
    eq_(d, pytool.time.as_utc(t))
    d = pytool.time.as_utc(d)
    eq_(d, pytool.time.as_utc(t))


def test_as_utc_naive():
    d = datetime.now()
    d2 = d + timedelta(seconds=time.altzone if pytool.time.is_dst(d)
            else time.timezone)
    d = pytool.time.as_utc(d)
    # Can't compare naive and aware datetimes, so we do it manually
    for field in ('year', 'month', 'day', 'hour', 'minute', 'second',
            'microsecond'):
        eq_(getattr(d, field), getattr(d2, field))


# These daylight savings tests are a bit sloppy, but oh well
def test_is_dst():
    if 'UTC' in time.tzname:
        raise SkipTest("Test doesn't work if server timezone is UTC")
    d = datetime(2000, 6, 1)
    eq_(pytool.time.is_dst(d), True)


def test_is_not_dst():
    if 'UTC' in time.tzname:
        raise SkipTest("Test doesn't work if server timezone is UTC")
    d = datetime(2000, 11, 30)
    eq_(pytool.time.is_dst(d), False)


def test_week_start():
    start = pytool.time.week_start(datetime.now())
    eq_(start.weekday(), 0)
    eq_(start.hour, 0)
    eq_(start.minute, 0)
    eq_(start.second, 0)
    eq_(start.microsecond, 0)


def test_week_seconds_start():
    secs = pytool.time.week_seconds(pytool.time.week_start(datetime.now()))
    eq_(secs, 0)


def test_week_seconds():
    start = pytool.time.week_start(datetime.now())
    for i in range(7):
        eq_(pytool.time.week_seconds(start + timedelta(days=i)),
                timedelta(days=i).total_seconds())


def test_week_seconds_to_datetime():
    for i in range(7):
        eq_(pytool.time.week_start(datetime.now()) + timedelta(days=i),
                pytool.time.week_seconds_to_datetime(
                    timedelta(days=i).total_seconds()))


def test_make_week_seconds():
    eq_(pytool.time.make_week_seconds(0, 1), 60*60)
    eq_(pytool.time.make_week_seconds(1, 0), 60*60*24)
    eq_(pytool.time.make_week_seconds(7, 0), 0)
    eq_(pytool.time.make_week_seconds(2, 1, 1, 1), 60*60*24*2 + 60*60 + 60 + 1)


def test_floor_minute():
    stamp = pytool.time.utcnow()
    eq_(pytool.time.floor_minute(stamp), datetime(stamp.year, stamp.month,
        stamp.day, stamp.hour, stamp.minute, tzinfo=stamp.tzinfo))


def test_floor_day():
    stamp = pytool.time.utcnow()
    eq_(pytool.time.floor_day(stamp),
            datetime(*stamp.date().timetuple()[:-3],
                tzinfo=pytool.time.UTC()))


def test_floor_week():
    stamp = pytool.time.utcnow()
    start = stamp - timedelta(days=stamp.weekday())
    eq_(pytool.time.floor_week(stamp),
            datetime(start.year, start.month, start.day,
                tzinfo=pytool.time.UTC()))


def test_floor_month():
    stamp = pytool.time.utcnow()
    eq_(pytool.time.floor_month(stamp),
            datetime(*(stamp.date().timetuple()[:2] + (1,)),
                tzinfo=pytool.time.UTC()))


def test_timer_init_works():
    pytool.time.Timer()


def test_timer_elapsed_works():
    with mock.patch('pytool.time.utcnow') as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 0, 0)
        t = pytool.time.Timer()
    with mock.patch('pytool.time.utcnow') as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 1, 0)
        eq_(t.elapsed, timedelta(seconds=60))
    with mock.patch('pytool.time.utcnow') as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 1, 0, 0)
        eq_(t.elapsed, timedelta(seconds=60*60))


def test_timer_mark_works():
    with mock.patch('pytool.time.utcnow') as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 0, 0)
        t = pytool.time.Timer()
    with mock.patch('pytool.time.utcnow') as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 1, 0)
        eq_(t.mark(), timedelta(seconds=60))
    with mock.patch('pytool.time.utcnow') as utcnow:
        utcnow.return_value = datetime(2010, 1, 1, 0, 3, 0)
        eq_(t.mark(), timedelta(seconds=2*60))


def test_ago_regular():
    unix = 14386000000
    stamp = pytool.time.fromutctimestamp(unix)
    # Previous stamp minus 1 day, 1 hour, 1 minute and 1 second
    ago = unix - (24*60*60) - (60*60) - 60 - 1
    ago = pytool.time.fromutctimestamp(ago)

    eq_(pytool.time.ago(stamp, days=1, hours=1, minutes=1, seconds=1), ago)


def test_ago_shorter():
    unix = 14386000000
    stamp = pytool.time.fromutctimestamp(unix)
    # Previous stamp minus 1 day, 1 hour, 1 minute and 1 second
    ago = unix - (24*60*60) - (60*60) - 60 - 1
    ago = pytool.time.fromutctimestamp(ago)

    eq_(pytool.time.ago(stamp, days=1, hrs=1, mins=1, secs=1), ago)


def test_ago_shorthand():
    unix = 14386000000
    stamp = pytool.time.fromutctimestamp(unix)
    # Previous stamp minus 1 day, 1 hour, 1 minute and 1 second
    ago = unix - (24*60*60) - (60*60) - 60 - 1
    ago = pytool.time.fromutctimestamp(ago)

    eq_(pytool.time.ago(stamp, d=1, h=1, m=1, s=1), ago)
