from datetime import datetime, timedelta

import mock
try:
    import bson
except ImportError:
    bson = None

import pytool
from .util import *


def test_as_json_datetime():
    n = datetime.now()
    eq_(pytool.json.as_json(n),
            '"{}"'.format(n.strftime('%a %b %d %Y %H:%M:%S %z')))


def test_as_json_datetime_with_tz():
    n = pytool.time.utcnow()
    eq_(pytool.json.as_json(n),
            '"{}"'.format(n.strftime('%a %b %d %Y %H:%M:%S %z')))


def test_as_json_ObjectId():
    if bson:
        b = bson.ObjectId()
        eq_(pytool.json.as_json(b), '"{}"'.format(b))


@raises(TypeError)
def test_as_json_bad():
    d = {'test': 1, 'two':type()}
    pytool.json.as_json(d)


@mock.patch('pytool.json.json.loads')
def test_from_json(loads):
    loads.return_value = '1'
    val = pytool.json.from_json(loads.return_value)
    eq_(val, loads.return_value)
    loads.assert_called_with(loads.return_value)


def test_as_json_with_bson():
    obj = pytool.json.bson.ObjectId()
    eq_(pytool.json.as_json(obj), pytool.json.as_json(str(obj)))


@raises(TypeError)
def test_as_json_with_bad():
    obj = object()
    pytool.json.as_json(obj)



