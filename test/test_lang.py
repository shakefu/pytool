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


def test_namespace_empty():
    ns = pytool.lang.Namespace()
    eq_(ns.as_dict(), {})


def test_namespace_flat():
    ns = pytool.lang.Namespace()
    ns.foo = 'foo'
    ns.bar = 'bar'
    eq_(ns.as_dict(), {'foo': 'foo', 'bar': 'bar'})


def test_namespace_singly_nested():
    ns = pytool.lang.Namespace()
    ns.foobar.foo = 'foo'
    ns.foobar.bar = 'bar'
    eq_(ns.as_dict(), {
        'foobar.foo': 'foo',
        'foobar.bar': 'bar',
        })


def test_namespace_deep():
    ns = pytool.lang.Namespace()
    ns.foo.bar.you = 'hello'
    eq_(ns.as_dict(), {'foo.bar.you': 'hello'})


def test_namespace_base_name():
    ns = pytool.lang.Namespace()
    ns.foo = 'bar'
    eq_(ns.as_dict('ns'), {'ns.foo': 'bar'})


def test_namespace_iterable():
    ns = pytool.lang.Namespace()
    ns.foo = 1
    ns.bar = 2
    ns.you.bar = 3
    dns = ns.as_dict()
    names = set(('foo', 'bar', 'you.bar'))
    values = set((1, 2, 3))
    for name, value in ns:
        ok_(name in names)
        ok_(value in values)
        eq_(value, dns[name])
        names.remove(name)
        values.remove(value)


def test_namespace_in():
    ns = pytool.lang.Namespace()
    ns.foo = True
    ns.hello.world.there = 'howdy'

    ok_('foo' in ns)
    ok_('hello.world' in ns)
    ok_('hello.world.there' in ns)
    ok_('world' in ns.hello)
    ok_('bar' not in ns)
    ok_('hello.banana' not in ns)

