from datetime import datetime

import mock
from nose import SkipTest
try:
    import bson
except ImportError:
    bson = None

import pytool
from .util import *


def test_as_json_datetime():
    n = datetime.now()
    eq_(pytool.json.as_json(n),
            '"{}"'.format(n.strftime('%a %b %d %Y %H:%M:%S %z').strip()))


def test_as_json_datetime_with_tz():
    n = pytool.time.utcnow()
    eq_(pytool.json.as_json(n),
            '"{}"'.format(n.strftime('%a %b %d %Y %H:%M:%S %z').strip()))


def test_as_json_ObjectId():
    if not bson:
        raise SkipTest("missing bson module")
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


def test_asdict_encodes():
    class Test(object):
        def _asdict(self):
            return {'_asdict': 1}

    eq_(pytool.json.as_json(Test()), '{"_asdict": 1}')


def test_for_json_hook_with_dict():
    class Test(object):
        def for_json(self):
            return {'for_json': 1}

    eq_(pytool.json.as_json(Test()), '{"for_json": 1}')


def test_for_json_hook_with_list():
    class Test(object):
        def for_json(self):
            return ['for_json']

    eq_(pytool.json.as_json(Test()), '["for_json"]')


def test_for_json_hook_nested():
    class Test(object):
        def for_json(self):
            return {'for_json': 1}

    class Test2(object):
        def for_json(self):
            return [Test()]

    eq_(pytool.json.as_json(Test2()), '[{"for_json": 1}]')


def test_for_json_hook_called_when_within_a_list_within_a_dict():
    class Test(object):
        def for_json(self):
            return {'for_json': 1}

    obj = {'list': [Test()]}
    eq_(pytool.json.as_json(obj), '{"list": [{"for_json": 1}]}')


def test_for_json_hook_called_when_dict_subclass_buried_in_objects():
    class Test(dict):
        def for_json(self):
            return {'for_json': 1}

    obj = {'list': [Test()]}
    eq_(pytool.json.as_json(obj), '{"list": [{"for_json": 1}]}')



