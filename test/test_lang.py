import inspect
from datetime import datetime, timedelta

import mock

import pytool
from .util import *


def test_get_name():
    frame = inspect.currentframe()
    eq_(pytool.lang.get_name(frame),
            'test.test_lang.test_get_name')
    del frame


def test_get_name_class():
    class Test(object):
        def test(self):
            frame = inspect.currentframe()
            eq_(pytool.lang.get_name(frame),
                    'test.test_lang.Test.test')
            del frame

    Test().test()


def test_classproperty():
    class Test(object):
        value = 'Test'
        @pytool.lang.classproperty
        def test(cls):
            return cls.value

    eq_(Test.test, Test.value)
    eq_(Test().test, Test().value)
    eq_(Test().test, Test.test)


def test_singleton():
    @pytool.lang.singleton
    class Singleton(object):
        pass
    eq_(id(Singleton()), id(Singleton()))
    ok_(Singleton() is Singleton())


def test_unset_false():
    eq_(pytool.lang.UNSET, False)
    eq_(pytool.lang.UNSET, None)
    eq_(pytool.lang.UNSET, 0)
    eq_(pytool.lang.UNSET, '')
    ok_(not bool(pytool.lang.UNSET))
    ok_(not pytool.lang.UNSET)


def test_unset_len():
    eq_(len(pytool.lang.UNSET), 0)


def test_unset_equal_to_unset():
    eq_(pytool.lang.UNSET, pytool.lang.UNSET)


def test_unset_not_true():
    eq_(pytool.lang.UNSET, 0)
    ok_(not (pytool.lang.UNSET == 'foo'))


def test_unset_empty():
    eq_(list(pytool.lang.UNSET), [])


def test_unset_iter():
    count = 0
    for i in pytool.lang.UNSET:
        count += 1
    eq_(count, 0)


def test_unset_repr():
    eq_(repr(pytool.lang.UNSET), 'UNSET')


def test_unset_instance():
    eq_(pytool.lang.UNSET(), pytool.lang.UNSET)


