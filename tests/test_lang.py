import copy
import gc
import inspect

import pytest
import simplejson

import pytool


@pytool.lang.hashed_singleton
class HashedSingleton(object):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def static():
        return "static"


@pytool.lang.singleton
class Singleton(object):
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def static():
        return "static"


def test_get_name():
    frame = inspect.currentframe()
    assert pytool.lang.get_name(frame) == "tests.test_lang.test_get_name"
    del frame


def test_get_name_class():
    class Test(object):
        def test(self):
            frame = inspect.currentframe()
            assert pytool.lang.get_name(frame) == "tests.test_lang.Test.test"
            del frame

    Test().test()


def test_get_name_class_method():
    class Test(object):
        @classmethod
        def test(cls):
            frame = inspect.currentframe()
            assert pytool.lang.get_name(frame) == "tests.test_lang.Test.test"
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

    assert Test().test == "tests.test_lang.Test.test"


def test_classproperty():
    class Test(object):
        value = "Test"

        @pytool.lang.classproperty
        def test(cls):
            return cls.value

    assert Test.test == Test.value
    assert Test().test == Test().value
    assert Test().test == Test.test


def test_singleton():
    @pytool.lang.singleton
    class Singleton(object):
        pass

    assert id(Singleton()) == id(Singleton())
    assert Singleton() is Singleton()


def test_unset_false():
    assert pytool.lang.UNSET == False  # noqa
    assert pytool.lang.UNSET == None  # noqa
    assert pytool.lang.UNSET == 0
    assert pytool.lang.UNSET == ""
    assert not bool(pytool.lang.UNSET)
    assert not pytool.lang.UNSET


def test_unset_len():
    assert len(pytool.lang.UNSET) == 0


def test_unset_equal_to_unset():
    assert pytool.lang.UNSET == pytool.lang.UNSET


def test_unset_not_true():
    assert pytool.lang.UNSET == 0
    assert not (pytool.lang.UNSET == "foo")


def test_unset_empty():
    assert list(pytool.lang.UNSET) == []


def test_unset_iter():
    count = 0
    for i in pytool.lang.UNSET:
        count += 1
    assert count == 0


def test_unset_repr():
    assert repr(pytool.lang.UNSET) == "UNSET"


def test_unset_instance():
    assert pytool.lang.UNSET() == pytool.lang.UNSET


def test_namespace_empty():
    ns = pytool.lang.Namespace()
    assert ns.as_dict() == {}


def test_namespace_flat():
    ns = pytool.lang.Namespace()
    ns.foo = "foo"
    ns.bar = "bar"
    assert ns.as_dict() == {"foo": "foo", "bar": "bar"}


def test_namespace_singly_nested():
    ns = pytool.lang.Namespace()
    ns.foobar.foo = "foo"
    ns.foobar.bar = "bar"
    assert ns.as_dict() == {
        "foobar.foo": "foo",
        "foobar.bar": "bar",
    }


def test_namespace_deep():
    ns = pytool.lang.Namespace()
    ns.foo.bar.you = "hello"
    assert ns.as_dict() == {"foo.bar.you": "hello"}


def test_namespace_base_name():
    ns = pytool.lang.Namespace()
    ns.foo = "bar"
    assert ns.as_dict("ns") == {"ns.foo": "bar"}


def test_namespace_with_list():
    ns = pytool.lang.Namespace()
    ns.foo = []
    ns.foo.append(pytool.lang.Namespace())
    ns.foo[0].bar = 1
    assert ns.as_dict("ns") == {"ns.foo": [{"bar": 1}]}


def test_namespace_iterable():
    ns = pytool.lang.Namespace()
    ns.foo = 1
    ns.bar = 2
    ns.you.bar = 3
    dns = ns.as_dict()
    names = set(("foo", "bar", "you.bar"))
    values = set((1, 2, 3))
    for name, value in ns:
        assert name in names
        assert value in values
        assert value == dns[name]
        names.remove(name)
        values.remove(value)


def test_namespace_in():
    ns = pytool.lang.Namespace()
    ns.foo = True
    ns.hello.world.there = "howdy"

    assert "foo" in ns
    assert "hello.world" in ns
    assert "hello.world.there" in ns
    assert "world" in ns.hello
    assert "bar" not in ns
    assert "hello.banana" not in ns


def test_namespace_contains_does_not_create_new_fields():
    ns = pytool.lang.Namespace()
    ns.a = "a"
    assert "a" in ns
    assert "b" not in ns.__dict__
    assert "b" not in ns
    # Make sure we didn't create an empty entry with the contains check
    assert "b" not in ns.__dict__
    assert ns.as_dict() == {"a": "a"}


def test_namespace_evaluates_to_false_when_empty():
    ns = pytool.lang.Namespace()
    assert bool(ns) is False
    assert not ns
    assert bool(ns.attr) is False
    assert not ns.attr


def test_namespace_evaluates_as_true_when_has_an_item():
    ns = pytool.lang.Namespace()
    ns.item = 1
    assert bool(ns) is True
    assert ns


def test_namespace_reprs_accurately_when_empty():
    ns = pytool.lang.Namespace()
    assert repr(ns) == "<Namespace({})>"


def test_namespace_instances_implement_descriptor_reads():
    class Descriptor(object):
        value = "Descriptor Value"

        def __get__(self, instance, owner):
            return self.value

    desc = Descriptor()
    ns = pytool.lang.Namespace()
    ns.desc = desc
    assert ns.desc == "Descriptor Value"
    desc.value = "New Value"
    assert ns.desc == "New Value"
    assert ns.as_dict() == {"desc": "New Value"}
    ns.desc = "Non Descriptor"
    assert ns.desc == "Non Descriptor"
    assert desc.value == "New Value"


def test_namespace_can_map_a_dict():
    obj = {"value": 1}
    ns = pytool.lang.Namespace(obj)
    assert ns.value == 1


def test_namespace_can_map_a_nested_dict():
    obj = {"top": {"value": 2}}
    ns = pytool.lang.Namespace(obj)
    assert ns.top.value == 2


def test_namespace_can_map_a_nested_list():
    obj = {"listed": [{"value": 1}, {"value": 2}, 3]}
    ns = pytool.lang.Namespace(obj)
    assert ns.listed[0].value == 1
    assert ns.listed[1].value == 2
    assert ns.listed[2] == 3


def test_namespace_can_map_a_nested_list_with_nested_dicts_complex():
    obj = {"top": {"nested": [{"obj": {"value": 1}}]}}
    ns = pytool.lang.Namespace(obj)
    assert ns.top.nested[0].obj.value == 1


def test_namespace_doesnt_accept_bad_key_names():
    obj = {"key-name": 1}
    with pytest.raises(AssertionError):
        pytool.lang.Namespace(obj)


def test_namespace_doesnt_accept_lists():
    obj = ["foo"]
    with pytest.raises(AssertionError):
        pytool.lang.Namespace(obj)


def test_namespace_doesnt_accept_ints():
    obj = 1
    with pytest.raises(AssertionError):
        pytool.lang.Namespace(obj)


def test_namespace_doesnt_accept_strings():
    obj = "foo"
    with pytest.raises(AssertionError):
        pytool.lang.Namespace(obj)


def test_namespace_doesnt_accept_namespaces():
    obj = pytool.lang.Namespace()
    with pytest.raises(AssertionError):
        pytool.lang.Namespace(obj)


def test_namespaces_allow_merging_multiple_dicts():
    obj = {"foo": 1}
    obj2 = {"bar": 2}
    ns = pytool.lang.Namespace()
    ns.from_dict(obj)
    ns.from_dict(obj2)

    assert ns.foo == 1
    assert ns.bar == 2


def test_namespaces_will_convert_dicts_in_lists():
    obj = {"foo": [{"bar": 1}]}
    ns = pytool.lang.Namespace()
    ns.from_dict(obj)

    assert ns.foo[0].bar == 1


def test_namespaces_work_with_dot_notation():
    obj = {"foo.bar": 1}
    ns = pytool.lang.Namespace(obj)
    assert ns.foo.bar == 1


def test_namespaces_coerce_lists():
    obj = {"alpha": {"0": "zero", "1": "one", "2": "two"}}
    ns = pytool.lang.Namespace(obj)
    assert ns.alpha == ["zero", "one", "two"]


def test_namespaces_coerce_lists_and_recurse():
    obj = {"alpha": {"0": "zero", "1": "one", "2": {"foo.bar": 2}}}
    ns = pytool.lang.Namespace(obj)
    assert ns.alpha[2].foo.bar == 2


def test_namespaces_reject_top_level_lists():
    obj = {"0": "zero", "1": "one", "2": "two"}
    with pytest.raises(AssertionError):
        pytool.lang.Namespace(obj)


def test_namespaces_allow_key_access():
    obj = {"foo": 1, "bar": 2}
    ns = pytool.lang.Namespace(obj)
    assert ns["foo"] == 1


def test_namespaces_allow_key_access_for_reserved_words():
    obj = {"foo": 1, "bar": 2, "in": 3}
    ns = pytool.lang.Namespace(obj)
    assert ns["in"] == 3


def test_namespaces_allow_key_access_for_nested_reserved_words():
    obj = {"foo": {"in": {"bar": 1}}}
    ns = pytool.lang.Namespace(obj)
    assert ns.foo["in"].bar == 1


def test_namespace_can_merge_dict_manually():
    ns = pytool.lang.Namespace({"foo": {"bar": 1, "fnord": 0}})
    ns2 = pytool.lang.Namespace({"foo": {"doot": 2, "bar": 3}})
    merge = ns.as_dict()
    merge.update(ns2.as_dict())
    ns = pytool.lang.Namespace(merge)
    assert ns.foo.doot == 2
    assert ns.foo.bar == 3
    assert ns.foo.fnord == 0


def test_namespace_for_json_simple():
    obj = {"foo": 1, "bar": 2}
    ns = pytool.lang.Namespace(obj)
    assert ns.for_json() == obj


def test_namespace_for_json_nested():
    obj = {"foo": {"bar": 1}}
    ns = pytool.lang.Namespace(obj)
    assert ns.for_json() == obj
    assert ns.as_dict() == {"foo.bar": 1}


def test_namespace_for_json_base_name():
    obj = {"foo": {"bar": 1}}
    ns = pytool.lang.Namespace(obj)
    assert ns.for_json("base") == {"base": obj}


def test_namespace_for_json_nested_list():
    obj = {"foo": [{"bar": {"fnord": 1}}]}
    ns = pytool.lang.Namespace(obj)
    assert ns.for_json() == obj


def test_namspace_for_json_simplejson_encode():
    obj = {"foo": {"bar": 1}}
    ns = pytool.lang.Namespace(obj)
    assert simplejson.dumps(ns, for_json=True) == '{"foo": {"bar": 1}}'


def test_keyspace_allows_item_assignment():
    ks = pytool.lang.Keyspace()
    ks["foo"] = 1
    ks["key-name"] = 2
    assert ks.as_dict() == {"foo": 1, "key-name": 2}


def test_keyspace_create_keyspace():
    ks = pytool.lang.Keyspace()
    ks.foo.bar = 1
    assert type(ks.foo) is pytool.lang.Keyspace


def test_keyspace_allows_getitem_traversal():
    ks = pytool.lang.Keyspace()
    ks["foo"].bar = 1
    assert ks.as_dict() == {"foo.bar": 1}


def test_keyspace_allows_getitem_traversal_with_nonattribute_names():
    ks = pytool.lang.Keyspace()
    ks["key-name"].bar = 1
    assert ks.as_dict() == {"key-name.bar": 1}


def test_keyspace_allows_getitem_traversal_with_nonattribute_names_deep():
    ks = pytool.lang.Keyspace()
    ks.foo["key-name"].bar = 1
    assert ks.as_dict() == {"foo.key-name.bar": 1}


def test_keyspace_allows_nested_item_assignment():
    ks = pytool.lang.Keyspace()
    ks.foo["bar"] = 1
    assert ks.as_dict() == {"foo.bar": 1}


def test_keyspace_copy_works():
    ks = pytool.lang.Keyspace()
    ks.foo["key-name"].bar = 1
    ks2 = copy.copy(ks)
    assert ks.as_dict() == ks2.as_dict()


def test_keyspace_reprs_accurately_when_empty():
    ns = pytool.lang.Keyspace()
    assert repr(ns) == "<Keyspace({})>"


def test_hashed_singleton_no_args():
    t = HashedSingleton()
    assert t is HashedSingleton()


def test_hashed_singleton_arg():
    t = HashedSingleton("t")
    assert t is HashedSingleton("t")
    assert t is not HashedSingleton("n")


def test_hashed_singleton_args():
    t = HashedSingleton("a", "b")
    assert t is not HashedSingleton("a", "a")
    assert t is not HashedSingleton("b", "a")
    assert t is not HashedSingleton("a", "b", "c")
    assert t is HashedSingleton("a", "b")


def test_hashed_singleton_kwargs():
    t = HashedSingleton(a="a", b="b")
    assert t is HashedSingleton(a="a", b="b")
    assert t is HashedSingleton(b="b", a="a")
    assert t is not HashedSingleton(a="a", b="a")
    assert t is not HashedSingleton(a="a", b="b", c="c")


def test_hashed_singleton_args_kwargs():
    t = HashedSingleton("a", "b", a="a", b="b")
    assert t is HashedSingleton("a", "b", a="a", b="b")


def test_hashed_singleton_weakref():
    t = HashedSingleton()
    assert t is HashedSingleton()

    # Grab the string representation which includes the object id
    ts = str(t)

    del t
    # Need to force collection here, otherwise Python is lazy
    gc.collect()

    # This should be a new instance of the singleton
    t2 = HashedSingleton()
    assert ts != str(t2), "{} != {}".format(ts, str(t2))


def test_hashed_singleton_preserves_staticmethods():
    assert HashedSingleton.static
    assert HashedSingleton.static() == "static"

    t = HashedSingleton()
    assert t.static
    assert t.static() == "static"


def test_singleton_no_args():
    s = Singleton()
    assert s is Singleton()


def test_singleton_args():
    s = Singleton("arg")
    assert s is Singleton("gra")


def test_singleton_kwarg():
    s = Singleton(kwarg="kwarg")
    assert s is Singleton(grawk="grawk")


def test_singleton_preserves_staticmethods():
    assert Singleton.static
    assert Singleton.static() == "static"

    t = Singleton()
    assert t.static
    assert t.static() == "static"


def test_unflatten():
    obj = {
        "nest": {"sub": 1},
        "dot.first": 1,
        "dot.second": 2,
        "arr.0": 3,
        "arr.1": 4,
        "arr.2": 5,
        "more": [{"down.first": 1}, {"down.second": 2}, 3],
        "bad.0": 0,
        "bad.1": 1,
        "bad.two": 2,
        "good": {
            0: "zero",
            1: "one",
            "2": "two",
            "3": "three",
        },
    }

    expected = {
        "more": [{"down": {"first": 1}}, {"down": {"second": 2}}, 3],
        "bad": {"0": 0, "1": 1, "two": 2},
        "dot": {"first": 1, "second": 2},
        "nest": {"sub": 1},
        "good": ["zero", "one", "two", "three"],
        "arr": [3, 4, 5],
    }

    result = pytool.lang.unflatten(obj)

    assert result == expected


def test_namespace_copy():
    a = pytool.lang.Namespace()
    a.foo = "one"
    a.bar = [1, 2, 3]
    b = a.copy()
    b.foo = "two"
    a.bar[0] = 10

    assert a.foo == "one"
    assert b.bar == [1, 2, 3]


def test_namespace_copy_deeper():
    a = pytool.lang.Namespace()
    a.foo = [[1, 2], [3, 4]]
    b = a.copy()
    b.foo[0][0] = 100

    assert a.foo == [[1, 2], [3, 4]]
    assert b.foo == [[100, 2], [3, 4]]


def test_namespace_copy_mut():
    ns = pytool.lang.Namespace()
    ns.foo.bar = 1
    ns2 = ns.copy()
    ns2.foo.bar = 2

    assert ns.foo.bar == 1


def test_namespace_copy_mut_deep():
    ns = pytool.lang.Namespace()
    ns.foo.bar.baz = 1
    ns2 = ns.copy()
    ns2.foo.bar.baz = 2

    assert ns.foo.bar.baz == 1


def test_namespace_copy_mut_list():
    ns = pytool.lang.Namespace()
    ns.foo = []
    ns.foo.append(pytool.lang.Namespace())
    ns.foo[0].bar.baz = 1

    ns2 = ns.copy()
    ns2.foo[0].bar.baz = 2

    assert ns.foo[0].bar.baz == 1


def test_namespace_copy_api_deep():
    ns = pytool.lang.Namespace()
    ns.foo.bar.baz = 1
    ns2 = copy.copy(ns)
    ns2.foo.bar.baz = 2

    assert ns.foo.bar.baz == 1


def test_namespace_copy_api_list():
    ns = pytool.lang.Namespace()
    ns.foo = []
    ns.foo.append(pytool.lang.Namespace())
    ns.foo[0].bar.baz = 1

    ns2 = copy.deepcopy(ns)
    ns2.foo[0].bar.baz = 2

    assert ns.foo[0].bar.baz == 1


def test_namespace_traverse():
    ns = pytool.lang.Namespace()
    ns.foo.bar = "foobar"
    val = ns.traverse(["foo", "bar"])

    assert val == "foobar"


def test_namespace_traverse_list():
    ns = pytool.lang.Namespace(
        {
            "foo": [
                pytool.lang.Namespace({"name": "john"}),
                pytool.lang.Namespace({"name": "jane"}),
            ]
        }
    )
    name = ns.traverse(["foo", 0, "name"])

    assert name == "john"


def test_namespace_traverse_dict():
    ns = pytool.lang.Namespace()
    ns.foo = {
        "first": pytool.lang.Namespace({"color": "red"}),
        "second": pytool.lang.Namespace({"color": "blue"}),
    }
    val = ns.traverse(["foo", "second", "color"])

    assert val == "blue"


def test_namespace_traverse_failure_creates_more_namespaces():
    ns = pytool.lang.Namespace()

    ns.traverse(["foo"])

    assert ns.as_dict() == {}


def test_namespace_simple_key_access_traversal():
    ns = pytool.lang.Namespace()
    ns.foo.bar = "blue"

    assert ns["foo.bar"] == "blue"


def test_namespace_list_key_access_traversal():
    ns = pytool.lang.Namespace()
    ns.foo = ["you", "blue"]

    assert ns["foo.0"] == "you"
    assert ns["foo.1"] == "blue"

    ns.nested = []
    ns2 = pytool.lang.Namespace()
    ns2.foo.bar = "you"
    ns.nested.append(ns2)

    assert ns["nested.0.foo.bar"] == "you"


def test_namespace_traversal_bad_list_index():
    ns = pytool.lang.Namespace()
    ns.foo = [1, 2]

    with pytest.raises(IndexError):
        ns["foo.2"]


def test_namespace_traversal_bad_key_index_creates_more_namespaces():
    ns = pytool.lang.Namespace()
    ns.one.two.three = 1
    assert ns["one.three"].as_dict() == {}


def test_namespace_traversal_str_key_list_raises_typeerror():
    ns = pytool.lang.Namespace()
    ns.foo = [1, 2]

    with pytest.raises(TypeError):
        ns["foo.1e9"]


def test_namespace_items():
    ns = pytool.lang.Namespace()
    ns.foo = "bar"
    ns.fooby = "foobar"

    ns_items = {k: v for k, v in ns.items()}

    assert ns_items == {"foo": "bar", "fooby": "foobar"}


def test_namespace_items_nested():
    ns = pytool.lang.Namespace()
    ns.foo.bar = "foobar"
    ns.fooby = "foobaz"

    ns_items = {k: v for k, v in ns.items()}

    assert ns_items == {"foo.bar": "foobar", "fooby": "foobaz"}
