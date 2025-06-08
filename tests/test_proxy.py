import pytest

import pytool


def test_list_proxy_instantiates_ok():
    a_list = []
    pytool.proxy.ListProxy(a_list)


def test_list_proxy_proxies_repr():
    c = [1, 2]
    p = pytool.proxy.ListProxy(c)
    assert repr(c) == repr(p)


def test_list_proxy_proxies_comparisons():
    c = [1, 2]
    a = [1, 2]
    b = [3, 4]
    p = pytool.proxy.ListProxy(c)
    assert (c <= a) == (p <= a)
    assert (c <= b) == (p <= b)
    assert (c >= a) == (p >= a)
    assert (c >= b) == (p >= b)
    assert (c < a) == (p < a)
    assert (c < b) == (p < b)
    assert (c > a) == (p > a)
    assert (c > b) == (p > b)
    assert (c != a) == (p != a)
    assert (c != b) == (p != b)


def test_list_proxy_comparison_operator_again():
    c = [1, 2]
    a = [1, 2]
    b = [3, 4]
    p = pytool.proxy.ListProxy(c)
    assert c == a
    assert p == a
    assert p == c
    assert p == p
    assert p == p
    assert not p == b
    assert not p != a
    assert p < b


def test_list_proxy_contains_operator():
    c = [1, 2]
    p = pytool.proxy.ListProxy(c)
    for i in range(4):
        assert (i in c) == (i in p)


def test_list_proxy_length_operator():
    c = [1, 2]
    p = pytool.proxy.ListProxy(c)
    assert len(c) == len(p)


def test_list_proxy_set_get_and_delete_items():
    c = [1, 2]
    p = pytool.proxy.ListProxy(c)
    assert c[0] == p[0]
    assert c[1] == p[1]
    p[0] = 3
    assert c == p
    assert c[0] == 3
    del p[0]
    assert c == p
    assert c[0] == 2


def test_list_proxy_slicing():
    c = [i for i in range(5)]
    p = pytool.proxy.ListProxy(c)
    s = p[1:3]
    assert s == [1, 2]
    assert isinstance(s, list)
    p[1:3] = [5, 10]
    assert p == c
    assert c[1:3] == [5, 10]
    p[1:3] = p
    assert p == c
    p[1:3] = range(5)
    assert p == c
    assert p[1:5] == [0, 1, 2, 3]
    del p[1:]
    assert p == c
    assert p == [0]


def test_list_proxy_addition():
    c = [1, 2]
    p = pytool.proxy.ListProxy(c)
    n = p + p
    assert n == [1, 2, 1, 2]
    assert isinstance(n, list)
    n = p + [3, 4]
    assert n == [1, 2, 3, 4]
    assert isinstance(n, list)
    n = p + range(2)
    assert n == [1, 2, 0, 1]
    assert isinstance(n, list)
    n = [3, 4] + p
    assert n == [3, 4, 1, 2]
    assert isinstance(n, list)
    n = range(2) + p
    assert n == [0, 1, 1, 2]
    assert isinstance(n, list)
    n = p.__radd__(p)
    assert n == [1, 2, 1, 2]
    assert isinstance(n, list)
    p += [3, 4]
    assert p == [1, 2, 3, 4]
    p += range(2)
    assert p == [1, 2, 3, 4, 0, 1]
    p += p
    assert p == [1, 2, 3, 4, 0, 1, 1, 2, 3, 4, 0, 1]
    assert c == p


def test_list_proxy_as_json():
    c = pytool.proxy.ListProxy([])
    c.append("foo")
    assert pytool.json.as_json(c) == '["foo"]'


def test_list_proxy_multiplication():
    c = [1, 2]
    p = pytool.proxy.ListProxy(c)
    n = p * 2
    assert n == c * 2
    assert n == [1, 2, 1, 2]
    p *= 2
    assert p == c
    assert p == [1, 2, 1, 2]


def test_list_proxy_mutable_methods():
    c = [1, 2]
    p = pytool.proxy.ListProxy(c)
    p.append(3)
    assert c == p
    assert p == [1, 2, 3]
    p.insert(0, 0)
    assert c == p
    assert p == [0, 1, 2, 3]
    p.pop()
    assert c == p
    assert p == [0, 1, 2]
    p.extend(p)
    assert c == p
    assert p == [0, 1, 2, 0, 1, 2]
    p.extend([1, 2])
    assert c == p
    assert p == [0, 1, 2, 0, 1, 2, 1, 2]


def test_dict_proxy_instantiates():
    d = {}
    p = pytool.proxy.DictProxy(d)
    assert d == p


def test_dict_proxy_repr():
    d = {"one": 1, "two": 2}
    p = pytool.proxy.DictProxy(d)
    assert repr(d) == repr(p)


def test_dict_proxy_compare_again():
    d = {"one": 1, "two": 2}
    p = pytool.proxy.DictProxy(d)
    assert d == p
    assert p == p


def test_dict_proxy_get_set_del_item():
    d = {"one": 1}
    p = pytool.proxy.DictProxy(d)
    assert d["one"] == p["one"]
    p["one"] = 1
    assert d["one"] == p["one"]
    assert d["one"] == 1
    del p["one"]
    assert d == p
    assert d == {}
    assert p == {}


def test_dict_proxy_missing_handling():
    class MissingProxy(pytool.proxy.DictProxy):
        def __missing__(self, key):
            return pytool.lang.UNSET

    d = {"one": 1, "two": 2}
    m = MissingProxy(d)
    assert m["three"] == pytool.lang.UNSET


def test_dict_proxy_clear():
    d = {"one": 1, "two": 2}
    p = pytool.proxy.DictProxy(d)
    p.clear()
    assert d == {}
    assert p == {}


def test_dict_proxy_copy():
    d = {"one": 1, "two": 2}
    p = pytool.proxy.DictProxy(d)
    c = p.copy()
    assert c is not d
    assert d == p
    assert d == c

    class Subclass(pytool.proxy.DictProxy):
        pass

    p = Subclass(d)
    c = p.copy()
    assert c is not d
    assert d == p
    assert d == c


def test_dict_proxy_update():
    d = {"one": 1, "two": 2}
    u = {"three": 3}
    p = pytool.proxy.DictProxy(d)
    p.update(p)
    assert d == p
    p.update(u)
    assert d == p
    assert p == {"one": 1, "two": 2, "three": 3}
    p.update(None)
    p.update([("four", 4)])
    assert d == p
    assert p == {"one": 1, "two": 2, "three": 3, "four": 4}

    class Items(object):
        def items(self):
            return [("five", 5)]

    p.update(Items())
    assert d == p
    assert p == {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    p.update(six=6)
    assert d == p
    assert p == {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def test_dict_proxy_get():
    d = {}
    p = pytool.proxy.DictProxy(d)
    assert p.get("none") is None
    assert p.get("none", 1) == 1
    assert p.setdefault("some", "hun") == "hun"
    assert p.get("some") == "hun"


def test_dict_proxy_pop():
    d = {"one": 1}
    p = pytool.proxy.DictProxy(d)
    assert p.pop("one") == 1
    assert p.pop("one" == 2, 2)
    d["one"] = 1
    assert p.popitem() == ("one", 1)
    assert d == {}
    assert d == p


def test_dict_proxy_iter():
    d = {"one": 1, "two": 2}
    p = pytool.proxy.DictProxy(d)
    assert sorted(list(iter(p))) == ["one", "two"]


def test_dict_proxy_as_json():
    d = pytool.proxy.DictProxy({})
    d["foo"] = "bar"
    assert pytool.json.as_json(d) == '{"foo": "bar"}'


def test_dict_proxy_raises_key_error():
    d = pytool.proxy.DictProxy({})

    with pytest.raises(KeyError):
        d["foo"]
