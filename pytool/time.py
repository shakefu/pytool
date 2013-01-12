"""
This module contains time related things that make life easier.
"""
# The regular 'import time' fails, because for some insane reason, Python lets
# a module import itself. This is a work around to import the non-relative
# module.
import importlib
time = importlib.import_module('time')

import calendar
import datetime

from pytool.lang import singleton


@singleton
class UTC(datetime.tzinfo):
    """ UTC timezone. This is necessary since Python doesn't include any
        explicit timezone objects in the standard library. This can be used
        to create timezone-aware datetime objects, which are a pain to work
        with, but a necessary evil sometimes.

        ::

            from datetime import datetime
            from pytool.time import UTC

            utc_now = datetime.now(UTC())

    """
    def utcoffset(self, stamp):
        return datetime.timedelta(0)

    def tzname(self, stamp):
        return "UTC"

    def dst(self, stamp):
        return datetime.timedelta(0)


def is_dst(stamp):
    """ Return ``True`` if `stamp` is daylight savings.

        :param datetime stamp: Datetime

    """
    return time.localtime(time.mktime(stamp.timetuple())).tm_isdst == 1


def utcnow():
    """ Return the current UTC time as a timezone-aware datetime. """
    return datetime.datetime.now(UTC())


def fromutctimestamp(stamp):
    """ Return a timezone-aware datetime object from a UTC unix timestamp.

        :param float stamp: Unix timestamp in UTC

        ::

            import time
            from pytool.time import fromutctimestamp

            utc_datetime = fromutctimestamp(time.time())

    """
    decimal = int(round(10**6 * (stamp - int(stamp))))
    stamp = time.gmtime(stamp)
    new_stamp = datetime.datetime(*(stamp[:6] + (decimal, UTC())))
    # Correct for Python's fucking terrible handling of daylight savings
    if stamp.tm_isdst:
        new_stamp -= datetime.timedelta(hours=1)
    return new_stamp


def toutctimestamp(stamp):
    """ Converts a naive datetime object to a UTC unix timestamp. This has an
        advantage over `time.mktime` in that it preserves the decimal portion
        of the timestamp when converting.

        :param datetime stamp: Datetime to convert

        ::

            from datetime import datetime
            from pytool.time import toutctimestamp

            utc_stamp = toutctimestamp(datetime.now())

    """
    decimal = (1.0 * stamp.microsecond / 10**6)
    if stamp.tzinfo:
        # Hooray, it's timezone aware, we are saved!
        return calendar.timegm(stamp.utctimetuple()) + decimal

    # We don't have a timezone... shit
    return time.mktime(stamp.timetuple()) + decimal


def as_utc(stamp):
    """ Converts any datetime (naive or aware) to UTC time.

        :param datetime stamp: Datetime to convert

        ::

            from datetime import datetime
            from pytool.time import as_utc

            utc_datetime = as_utc(datetime.now())

    """
    return fromutctimestamp(toutctimestamp(stamp))


def trim_time(stamp):
    """ Trims the time portion off a timestamp, leaving the date intact.
        Returns a datetime of the same date, set to 00:00:00 hours. Preserves
        timezone information.

        :param datetime stamp: Timestamp to trim
        :returns: Trimmed timestamp

    """
    return datetime.datetime(*stamp.date().timetuple()[:-3],
            tzinfo=stamp.tzinfo)


def week_start(stamp):
    """ Return the start of the week containing *stamp*.

        .. versionchanged:: 2.0
           Preserves timezone information.

        :param datetime stamp: Timestamp

    """
    stamp = stamp - datetime.timedelta(days=stamp.weekday())
    stamp = trim_time(stamp)
    return stamp


def week_seconds(stamp):
    """ Return *stamp* converted to seconds since 00:00 Monday.

        :param datetime stamp: Timestamp to convert

    """
    difference = stamp - week_start(stamp)
    return int(difference.total_seconds())


def week_seconds_to_datetime(seconds):
    """ Return the datetime that is *seconds* from the start of this week.

        :param int seconds: Seconds

    """
    return (week_start(datetime.datetime.now())
            + datetime.timedelta(seconds=seconds))


def make_week_seconds(day, hour, minute=0, seconds=0):
    """ Return :func:`week_seconds` for the given *day* of the week, *hour*
        and *minute*.

        :param int day: Zero-indexed day of the week
        :param int hour: Zero-indexed 24-hour
        :param int minute: Minute (default: ``0``)
        :param int seconds: Seconds (default: ``0``)

    """
    stamp = week_start(datetime.datetime.now())
    stamp += datetime.timedelta(days=day)
    stamp = datetime.datetime.combine(stamp.date(),
            datetime.time(hour, minute, seconds))
    return week_seconds(stamp)


def floor_minute(stamp=None):
    """ Return `stamp` floored to the current minute. If no `stamp` is
        specified, the current time is used. Preserves timezone information.

        .. versionadded:: 2.0

        :param datetime stamp: `datetime` object to floor (default: now)

    """
    stamp = stamp - datetime.timedelta(seconds=stamp.second,
            microseconds=stamp.microsecond)
    return stamp


def floor_day(stamp=None):
    """ Return `stamp` floored to the current day. If no `stamp` is specified,
        the current time is used. This is similar to the
        :meth:`~datetime.datetime.date` method, but returns a
        :class:`~datetime.datetime` object, instead of a
        :class:`~datetime.date` object.

        This is the same as :func:`~pytool.time.trim_time`.

        .. versionchanged:: 2.0
           Preserves timezone information if it exists, and uses
           :func:`pytool.time.utcnow` instead of :meth:`datetime.datetime.now`
           if `stamp` is not given.

        :param datetime stamp: `datetime` object to floor (default: now)

    """
    stamp = stamp or utcnow()
    return trim_time(stamp)


def floor_week(stamp=None):
    """ Return `stamp` floored to the current week. If no `stamp` is specified,
        the current time is used. Preserves timezone information.

        This is the same as :func:`~pytool.time.week_start`

        .. versionadded:: 2.0

        :param datetime stamp: `datetime` object to floor (default now:)

    """
    stamp = stamp or utcnow()
    return week_start(stamp)


def floor_month(stamp=None):
    """ Return `stamp` floored to the current month. If no `stamp` is specified,
        the current time is used.

        .. versionchanged:: 2.0
           Preserves timezone information if it exists, and uses
           :func:`pytool.time.utcnow` instead of :meth:`datetime.datetime.now`
           if `stamp` is not given.

        :param datetime stamp: `datetime` object to floor (default: now)

    """
    stamp = stamp or utcnow()
    return datetime.datetime(stamp.year, stamp.month, 1, tzinfo=stamp.tzinfo)


