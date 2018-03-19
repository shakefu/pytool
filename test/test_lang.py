import gc
import inspect

import pytool
from .util import eq_, ok_


@pytool.lang.hashed_singleton
class HashedSingleton(object):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def static():
        return 'static'


@pytool.lang.singleton
class Singleton(object):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def static():
        return 'static'


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


def test_get_name_class_method():
    class Test(object):
        @classmethod
        def test(cls):
            frame = inspect.currentframe()
            eq_(pytool.lang.get_name(frame),
                    'test.test_lang.Test.test')
            del frame

    Test.test()


def test_get_name_class_property():
    class Test(object):
        @property
        def test(self):
            frame = inspect.currentframe()
            this_name = pytool.lang.get_name(frame)
            del frame
            return this_name
    eq_(Test().test, 'test.test_lang.Test.test')


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


def test_namespace_evaluates_to_false_when_empty():
    ns = pytool.lang.Namespace()
    eq_(bool(ns), False)
    ok_(not ns)
    eq_(bool(ns.attr), False)
    ok_(not ns.attr)


def test_namespace_evaluates_as_true_when_has_an_item():
    ns = pytool.lang.Namespace()
    ns.item = 1
    eq_(bool(ns), True)
    ok_(ns)


def test_namespace_reprs_accurately_when_empty():
    ns = pytool.lang.Namespace()
    eq_(repr(ns), '<Namespace({})>')


def test_namespace_instances_implement_descriptor_reads():
    class Descriptor(object):
        value = 'Descriptor Value'
        def __get__(self, instance, owner):
            return self.value

    desc = Descriptor()
    ns = pytool.lang.Namespace()
    ns.desc = desc
    eq_(ns.desc, 'Descriptor Value')
    desc.value = 'New Value'
    eq_(ns.desc, 'New Value')
    eq_(ns.as_dict(), {'desc': 'New Value'})
    ns.desc = 'Non Descriptor'
    eq_(ns.desc, 'Non Descriptor')
    eq_(desc.value, 'New Value')


def test_hashed_singleton_no_args():
    t = HashedSingleton()
    ok_(t is HashedSingleton())


def test_hashed_singleton_arg():
    t = HashedSingleton('t')
    ok_(t is HashedSingleton('t'))
    ok_(t is not HashedSingleton('n'))


def test_hashed_singleton_args():
    t = HashedSingleton('a', 'b')
    ok_(t is not HashedSingleton('a', 'a'))
    ok_(t is not HashedSingleton('b', 'a'))
    ok_(t is not HashedSingleton('a', 'b', 'c'))
    ok_(t is HashedSingleton('a', 'b'))


def test_hashed_singleton_kwargs():
    t = HashedSingleton(a='a', b='b')
    ok_(t is HashedSingleton(a='a', b='b'))
    ok_(t is HashedSingleton(b='b', a='a'))
    ok_(t is not HashedSingleton(a='a', b='a'))
    ok_(t is not HashedSingleton(a='a', b='b', c='c'))


def test_hashed_singleton_args_kwargs():
    t = HashedSingleton('a', 'b', a='a', b='b')
    ok_(t is HashedSingleton('a', 'b', a='a', b='b'))


def test_hashed_singleton_weakref():
    t = HashedSingleton()
    ok_(t is HashedSingleton())

    # Grab the string representation which includes the object id
    ts = str(t)

    del t
    # Need to force collection here, otherwise Python is lazy
    gc.collect()

    # This should be a new instance of the singleton
    t2 = HashedSingleton()
    ok_(ts != str(t2), "{} != {}".format(ts, str(t2)))


def test_hashed_singleton_preserves_staticmethods():
    ok_(HashedSingleton.static)
    eq_(HashedSingleton.static(), 'static')

    t = HashedSingleton()
    ok_(t.static)
    eq_(t.static(), 'static')


def test_singleton_no_args():
    s = Singleton()
    ok_(s is Singleton())


def test_singleton_args():
    s = Singleton('arg')
    ok_(s is Singleton('gra'))


def test_singleton_kwarg():
    s = Singleton(kwarg='kwarg')
    ok_(s is Singleton(grawk='grawk'))

def test_singleton_preserves_staticmethods():
    ok_(Singleton.static)
    eq_(Singleton.static(), 'static')

    t = Singleton()
    ok_(t.static)
    eq_(t.static(), 'static')
