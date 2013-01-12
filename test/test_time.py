import time
import inspect
import calendar
from datetime import datetime, timedelta

import mock
try:
    import bson
except ImportError:
    bson = None

import pytool
from .util import *


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


def test_as_utc_naive():
    d = datetime.now()
    d2 = d + timedelta(seconds=time.altzone if pytool.time.is_dst(d)
            else time.timezone)
    d = pytool.time.as_utc(d)
    # Can't compare naive and aware datetimes, so we do it manually
    for field in ('year', 'month', 'day', 'hour', 'minute', 'second',
            'microsecond'):
        eq_(getattr(d, field), getattr(d2, field))


def test_is_dst():
    d = datetime.now()
    d2 = d - timedelta(days=365/2, hours=12)
    eq_(pytool.time.is_dst(d), not pytool.time.is_dst(d2))
    eq_(not pytool.time.is_dst(d), pytool.time.is_dst(d2))


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
    for i in xrange(7):
        eq_(pytool.time.week_seconds(start + timedelta(days=i)),
                timedelta(days=i).total_seconds())


def test_week_seconds_to_datetime():
    for i in xrange(7):
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

