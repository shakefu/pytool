import gc
import copy
import inspect

import pytool
from .util import eq_, ok_, raises


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


def test_namespace_with_list():
    ns = pytool.lang.Namespace()
    ns.foo = []
    ns.foo.append(pytool.lang.Namespace())
    ns.foo[0].bar = 1
    eq_(ns.as_dict('ns'), {'ns.foo': [{'bar': 1}]})


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


def test_namespace_can_map_a_dict():
    obj = {'value': 1}
    ns = pytool.lang.Namespace(obj)
    eq_(ns.value, 1)


def test_namespace_can_map_a_nested_dict():
    obj = {'top': {'value': 2}}
    ns = pytool.lang.Namespace(obj)
    eq_(ns.top.value, 2)


def test_namespace_can_map_a_nested_list():
    obj = {'listed': [{'value': 1}, {'value': 2}, 3]}
    ns = pytool.lang.Namespace(obj)
    eq_(ns.listed[0].value, 1)
    eq_(ns.listed[1].value, 2)
    eq_(ns.listed[2], 3)


def test_namespace_can_map_a_nested_list_with_nested_dicts_complex():
    obj = {'top': {'nested': [{'obj': {'value': 1}}]}}
    ns = pytool.lang.Namespace(obj)
    eq_(ns.top.nested[0].obj.value, 1)


@raises(AssertionError)
def test_namespace_doesnt_accept_bad_key_names():
    obj = {'key-name': 1}
    pytool.lang.Namespace(obj)


@raises(AssertionError)
def test_namespace_doesnt_accept_lists():
    obj = ['foo']
    pytool.lang.Namespace(obj)


@raises(AssertionError)
def test_namespace_doesnt_accept_ints():
    obj = 1
    pytool.lang.Namespace(obj)


@raises(AssertionError)
def test_namespace_doesnt_accept_strings():
    obj = 'foo'
    pytool.lang.Namespace(obj)


@raises(AssertionError)
def test_namespace_doesnt_accept_namespaces():
    obj = pytool.lang.Namespace()
    pytool.lang.Namespace(obj)


def test_namespaces_allow_merging_multiple_dicts():
    obj = {'foo': 1}
    obj2 = {'bar': 2}
    ns = pytool.lang.Namespace()
    ns.from_dict(obj)
    ns.from_dict(obj2)

    eq_(ns.foo, 1)
    eq_(ns.bar, 2)


def test_namespaces_will_convert_dicts_in_lists():
    obj = {'foo': [{'bar': 1}]}
    ns = pytool.lang.Namespace()
    ns.from_dict(obj)

    eq_(ns.foo[0].bar, 1)


def test_namespaces_work_with_dot_notation():
    obj = {'foo.bar': 1}
    ns = pytool.lang.Namespace(obj)
    eq_(ns.foo.bar, 1)


def test_namespaces_coerce_lists():
    obj = {'alpha': {'0': 'zero', '1': 'one', '2': 'two'}}
    ns = pytool.lang.Namespace(obj)
    eq_(ns.alpha, ['zero', 'one', 'two'])


def test_namespaces_coerce_lists_and_recurse():
    obj = {'alpha': {'0': 'zero', '1': 'one', '2': {'foo.bar': 2}}}
    ns = pytool.lang.Namespace(obj)
    eq_(ns.alpha[2].foo.bar, 2)


@raises(AssertionError)
def test_namespaces_reject_top_level_lists():
    obj = {'0': 'zero', '1': 'one', '2': 'two'}
    pytool.lang.Namespace(obj)


def test_namespaces_allow_key_access():
    obj = {'foo': 1, 'bar': 2}
    ns = pytool.lang.Namespace(obj)
    eq_(ns['foo'], 1)


def test_namespaces_allow_key_access_for_reserved_words():
    obj = {'foo': 1, 'bar': 2, 'in': 3}
    ns = pytool.lang.Namespace(obj)
    eq_(ns['in'], 3)


def test_namespaces_allow_key_access_for_nested_reserved_words():
    obj = {'foo': {'in': {'bar': 1}}}
    ns = pytool.lang.Namespace(obj)
    eq_(ns.foo['in'].bar, 1)


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


def test_unflatten():
    obj = {
        'nest': {
            'sub': 1
            },
        'dot.first': 1,
        'dot.second': 2,
        'arr.0': 3,
        'arr.1': 4,
        'arr.2': 5,
        'more': [{'down.first': 1}, {'down.second': 2}, 3],
        'bad.0': 0,
        'bad.1': 1,
        'bad.two': 2,
        'good': {
            0: 'zero',
            1: 'one',
            '2': 'two',
            '3': 'three',
            }
        }

    expected = {
        'more': [{'down': {'first': 1}}, {'down': {'second': 2}}, 3],
        'bad': {'0': 0, '1': 1, 'two': 2},
        'dot': {'first': 1, 'second': 2},
        'nest': {'sub': 1},
        'good': ['zero', 'one', 'two', 'three'],
        'arr': [3, 4, 5]
        }

    result = pytool.lang.unflatten(obj)

    eq_(result, expected)


def test_namespace_copy():
    a = pytool.lang.Namespace()
    a.foo = 'one'
    a.bar = [1, 2, 3]
    b = a.copy()
    b.foo = 'two'
    a.bar[0] = 10

    eq_(a.foo, 'one')
    eq_(b.bar, [1, 2, 3])


def test_namespace_copy_deeper():
    a = pytool.lang.Namespace()
    a.foo = [[1, 2], [3, 4]]
    b = a.copy()
    b.foo[0][0] = 100

    eq_(a.foo, [[1, 2], [3, 4]])
    eq_(b.foo, [[100, 2], [3, 4]])


def test_namespace_copy_mut():
    ns = pytool.lang.Namespace()
    ns.foo.bar = 1
    ns2 = ns.copy()
    ns2.foo.bar = 2

    eq_(ns.foo.bar, 1)


def test_namespace_copy_mut_deep():
    ns = pytool.lang.Namespace()
    ns.foo.bar.baz = 1
    ns2 = ns.copy()
    ns2.foo.bar.baz = 2

    eq_(ns.foo.bar.baz, 1)


def test_namespace_copy_mut_list():
    ns = pytool.lang.Namespace()
    ns.foo = []
    ns.foo.append(pytool.lang.Namespace())
    ns.foo[0].bar.baz = 1

    ns2 = ns.copy()
    ns2.foo[0].bar.baz = 2

    eq_(ns.foo[0].bar.baz, 1)


def test_namespace_copy_api_deep():
    ns = pytool.lang.Namespace()
    ns.foo.bar.baz = 1
    ns2 = copy.copy(ns)
    ns2.foo.bar.baz = 2

    eq_(ns.foo.bar.baz, 1)


def test_namespace_copy_api_list():
    ns = pytool.lang.Namespace()
    ns.foo = []
    ns.foo.append(pytool.lang.Namespace())
    ns.foo[0].bar.baz = 1

    ns2 = copy.deepcopy(ns)
    ns2.foo[0].bar.baz = 2

    eq_(ns.foo[0].bar.baz, 1)


def test_namespace_traverse():
    ns = pytool.lang.Namespace()
    ns.foo.bar = "foobar"
    val = ns.traverse(["foo", "bar"])

    eq_(val, "foobar")


def test_namespace_traverse_list():
    ns = pytool.lang.Namespace({"foo":
                                [pytool.lang.Namespace({"name": "john"}),
                                 pytool.lang.Namespace({"name": "jane"})]})
    name = ns.traverse(["foo", 0, "name"])

    eq_(name, "john")


def test_namespace_traverse_dict():
    ns = pytool.lang.Namespace()
    ns.foo = {"first": pytool.lang.Namespace({"color": "red"}),
              "second": pytool.lang.Namespace({"color": "blue"})}
    val = ns.traverse(["foo", "second", "color"])

    eq_(val, "blue")


def test_namespace_traverse_failure_creates_more_namespaces():
    ns = pytool.lang.Namespace()

    ns.traverse(["foo"])

    eq_(ns.as_dict(), {})


def test_namespace_simple_key_access_traversal():
    ns = pytool.lang.Namespace()
    ns.foo.bar = 'blue'

    eq_(ns['foo.bar'], 'blue')


def test_namespace_list_key_access_traversal():
    ns = pytool.lang.Namespace()
    ns.foo = ['you', 'blue']

    eq_(ns['foo.0'], 'you')
    eq_(ns['foo.1'], 'blue')

    ns.nested = []
    ns2 = pytool.lang.Namespace()
    ns2.foo.bar = 'you'
    ns.nested.append(ns2)

    eq_(ns['nested.0.foo.bar'], 'you')


@raises(IndexError)
def test_namespace_traversal_bad_list_index():
    ns = pytool.lang.Namespace()
    ns.foo = [1, 2]

    ns['foo.2']


def test_namespace_traversal_bad_key_index_creates_more_namespaces():
    ns = pytool.lang.Namespace()
    ns.one.two.three = 1
    eq_(ns['one.three'].as_dict(), {})


@raises(TypeError)
def test_namespace_traversal_str_key_list_raises_typeerror():
    ns = pytool.lang.Namespace()
    ns.foo = [1, 2]

    ns['foo.1e9']


def test_namespace_items():
    ns = pytool.lang.Namespace()
    ns.foo = "bar"
    ns.fooby = "foobar"

    ns_items = {k: v for k, v in ns.items()}

    eq_(ns_items, {"foo": "bar", "fooby": "foobar"})


def test_namespace_items_nested():
    ns = pytool.lang.Namespace()
    ns.foo.bar = "foobar"
    ns.fooby = "foobaz"

    ns_items = {k: v for k, v in ns.items()}

    eq_(ns_items, {"foo.bar": "foobar", "fooby": "foobaz"})
