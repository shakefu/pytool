import six

import pytool
from .util import eq_, ok_, raises, SkipTest


def test_list_proxy_instantiates_ok():
    a_list = []
    pytool.proxy.ListProxy(a_list)


def test_list_proxy_proxies_repr():
    l = [1, 2]
    p = pytool.proxy.ListProxy(l)
    eq_(repr(l), repr(p))


def test_list_proxy_proxies_comparisons():
    l = [1, 2]
    a = [1, 2]
    b = [3, 4]
    p = pytool.proxy.ListProxy(l)
    eq_(l == a, p == a)
    eq_(l == b, p == b)
    eq_(l <= a, p <= a)
    eq_(l <= b, p <= b)
    eq_(l >= a, p >= a)
    eq_(l >= b, p >= b)
    eq_(l < a, p < a)
    eq_(l < b, p < b)
    eq_(l > a, p > a)
    eq_(l > b, p > b)
    eq_(l != a, p != a)
    eq_(l != b, p != b)


def test_list_proxy_comparison_operator():
    if six.PY3:
        raise SkipTest('Python 2')
    l = [1, 2]
    a = [1, 2]
    b = [3, 4]
    p = pytool.proxy.ListProxy(l)
    eq_(cmp(l, a), cmp(p, a))
    eq_(cmp(l, b), cmp(p, b))
    eq_(cmp(l, 'foo'), cmp(p, 'foo'))
    eq_(cmp(p, a), p.__cmp__(a))


def test_list_proxy_comparison_operator_again():
    l = [1, 2]
    a = [1, 2]
    b = [3, 4]
    p = pytool.proxy.ListProxy(l)
    eq_(l, a)
    eq_(p, a)
    eq_(p, l)
    eq_(p, p)
    ok_(p == p)
    ok_(not p == b)
    ok_(not p != a)
    ok_(p < b)


def test_list_proxy_contains_operator():
    l = [1, 2]
    p = pytool.proxy.ListProxy(l)
    for i in range(4):
        eq_(i in l, i in p)


def test_list_proxy_length_operator():
    l = [1, 2]
    p = pytool.proxy.ListProxy(l)
    eq_(len(l), len(p))


def test_list_proxy_set_get_and_delete_items():
    l = [1, 2]
    p = pytool.proxy.ListProxy(l)
    eq_(l[0], p[0])
    eq_(l[1], p[1])
    p[0] = 3
    eq_(l, p)
    eq_(l[0], 3)
    del p[0]
    eq_(l, p)
    eq_(l[0], 2)


def test_list_proxy_slicing():
    l = [i for i in range(5)]
    p = pytool.proxy.ListProxy(l)
    s = p[1:3]
    eq_(s, [1, 2])
    ok_(isinstance(s, list))
    p[1:3] = [5, 10]
    eq_(p, l)
    eq_(l[1:3], [5, 10])
    p[1:3] = p
    eq_(p, l)
    p[1:3] = range(5)
    eq_(p, l)
    eq_(p[1:5], [0, 1, 2, 3])
    del p[1:]
    eq_(p, l)
    eq_(p, [0])


def test_list_proxy_addition():
    l = [1, 2]
    p = pytool.proxy.ListProxy(l)
    n = p + p
    eq_(n, [1, 2, 1, 2])
    ok_(isinstance(n, list))
    n = p + [3, 4]
    eq_(n, [1, 2, 3, 4])
    ok_(isinstance(n, list))
    n = p + range(2)
    eq_(n, [1, 2, 0, 1])
    ok_(isinstance(n, list))
    n = [3, 4] + p
    eq_(n, [3, 4, 1, 2])
    ok_(isinstance(n, list))
    n = range(2) + p
    eq_(n, [0, 1, 1, 2])
    ok_(isinstance(n, list))
    n = p.__radd__(p)
    eq_(n, [1, 2, 1, 2])
    ok_(isinstance(n, list))
    p += [3, 4]
    eq_(p, [1, 2, 3, 4])
    p += range(2)
    eq_(p, [1, 2, 3, 4, 0, 1])
    p += p
    eq_(p, [1, 2, 3, 4, 0, 1, 1, 2, 3, 4, 0, 1])
    eq_(l, p)


def test_list_proxy_as_json():
    l = pytool.proxy.ListProxy([])
    l.append('foo')
    eq_(pytool.json.as_json(l), '["foo"]')


def test_list_proxy_multiplication():
    l = [1, 2]
    p = pytool.proxy.ListProxy(l)
    n = p * 2
    eq_(n, l * 2)
    eq_(n, [1, 2, 1, 2])
    p *= 2
    eq_(p, l)
    eq_(p, [1, 2, 1, 2])


def test_list_proxy_mutable_methods():
    l = [1, 2]
    p = pytool.proxy.ListProxy(l)
    p.append(3)
    eq_(l, p)
    eq_(p, [1, 2, 3])
    p.insert(0, 0)
    eq_(l, p)
    eq_(p, [0, 1, 2, 3])
    p.pop()
    eq_(l, p)
    eq_(p, [0, 1, 2])
    p.extend(p)
    eq_(l, p)
    eq_(p, [0, 1, 2, 0, 1, 2])
    p.extend([1, 2])
    eq_(l, p)
    eq_(p, [0, 1, 2, 0, 1, 2, 1, 2])


def test_dict_proxy_instantiates():
    d = {}
    p = pytool.proxy.DictProxy(d)
    eq_(d, p)


def test_dict_proxy_repr():
    d = {'one': 1, 'two': 2}
    p = pytool.proxy.DictProxy(d)
    eq_(repr(d), repr(p))


def test_dict_proxy_compare():
    if six.PY3:
        raise SkipTest("Python 2")
    d = {'one': 1, 'two': 2}
    p = pytool.proxy.DictProxy(d)
    eq_(cmp(p, d), cmp(d, d))
    eq_(p.__cmp__(d), cmp(d, d))
    eq_(p.__cmp__(p), cmp(p, p))


def test_dict_proxy_compare_again():
    d = {'one': 1, 'two': 2}
    p = pytool.proxy.DictProxy(d)
    eq_(d, p)
    eq_(p, p)


def test_dict_proxy_get_set_del_item():
    d = {'one': 1}
    p = pytool.proxy.DictProxy(d)
    eq_(d['one'], p['one'])
    p['one'] = 1
    eq_(d['one'], p['one'])
    eq_(d['one'], 1)
    del p['one']
    eq_(d, p)
    eq_(d, {})
    eq_(p, {})


def test_dict_proxy_missing_handling():
    class MissingProxy(pytool.proxy.DictProxy):
        def __missing__(self, key):
            return pytool.lang.UNSET
    d = {'one': 1, 'two': 2}
    m = MissingProxy(d)
    eq_(m['three'], pytool.lang.UNSET)


def test_dict_proxy_clear():
    d = {'one': 1, 'two': 2}
    p = pytool.proxy.DictProxy(d)
    p.clear()
    eq_(d, {})
    eq_(p, {})


def test_dict_proxy_copy():
    d = {'one': 1, 'two': 2}
    p = pytool.proxy.DictProxy(d)
    c = p.copy()
    ok_(c is not d)
    eq_(d, p)
    eq_(d, c)

    class Subclass(pytool.proxy.DictProxy):
        pass

    p = Subclass(d)
    c = p.copy()
    ok_(c is not d)
    eq_(d, p)
    eq_(d, c)


def test_dict_proxy_update():
    d = {'one': 1, 'two': 2}
    u = {'three': 3}
    p = pytool.proxy.DictProxy(d)
    p.update(p)
    eq_(d, p)
    p.update(u)
    eq_(d, p)
    eq_(p, {'one': 1, 'two': 2, 'three': 3})
    p.update(None)
    p.update([('four', 4)])
    eq_(d, p)
    eq_(p, {'one': 1, 'two': 2, 'three': 3, 'four': 4})
    class Items(object):
        def items(self):
            return [('five', 5)]
    p.update(Items())
    eq_(d, p)
    eq_(p, {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5})
    p.update(six=6)
    eq_(d, p)
    eq_(p, {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6})


def test_dict_proxy_get():
    d = {}
    p = pytool.proxy.DictProxy(d)
    eq_(p.get('none'), None)
    eq_(p.get('none', 1), 1)
    eq_(p.setdefault('some', 'hun'), 'hun')
    eq_(p.get('some'), 'hun')


def test_dict_proxy_pop():
    d = {'one': 1}
    p = pytool.proxy.DictProxy(d)
    eq_(p.pop('one'), 1)
    eq_(p.pop('one', 2), 2)
    d['one'] = 1
    eq_(p.popitem(), ('one', 1))
    eq_(d, {})
    eq_(d, p)


def test_dict_proxy_iter():
    d = {'one': 1, 'two': 2}
    p = pytool.proxy.DictProxy(d)
    eq_(sorted(list(iter(p))), ['one', 'two'])


def test_dict_proxy_as_json():
    d = pytool.proxy.DictProxy({})
    d['foo'] = 'bar'
    eq_(pytool.json.as_json(d), '{"foo": "bar"}')


@raises(KeyError)
def test_dict_proxy_raises_key_error():
    d = pytool.proxy.DictProxy({})
    d['foo']

