"""
This module contains items that are "missing" from the Python standard library,
that do miscelleneous things.
"""
import inspect
import weakref
import functools


def get_name(frame):
    """ Gets the name of the passed frame.

        :warning: It's very important to delete a stack frame after you're done
               using it, as it can cause circular references that prevents
               garbage collection.

        :param frame: Stack frame to inspect.
        :returns: Name of the frame in the form *module.class.method*.

    """
    module = inspect.getmodule(frame)

    name = frame.f_code.co_name
    if frame.f_code.co_varnames:
        # Does this method belong to a class?
        try:
            varname = frame.f_code.co_varnames[0]
            # The class or instance should be the first argument,
            # unless it was otherwise munged by a decorator or is a
            # @staticmethod
            maybe_cls = frame.f_locals[varname]

            # Get the actual method, if it exists on the class
            maybe_func = getattr(maybe_cls, frame.f_code.co_name)

            # If we have self, or a classmethod, we need the class name
            if (varname == 'self' or maybe_func.im_self == maybe_cls):
                cls_name = (getattr(maybe_cls, '__name__', None)
                        or getattr(getattr(maybe_cls, '__class__', None),
                            '__name__', None))

                if cls_name:
                    name =  "%s.%s" % (cls_name, name)
                    module = maybe_cls.__module__
        except (KeyError, AttributeError):
            # Probably not a class method, so fuck it
            pass

    if module:
        if not isinstance(module, basestring):
            module = module.__name__
        if name != '<module>':
            return "%s.%s" % (module, name)
        else:
            return module
    else:
        return name


def classproperty(func):
    """
    Makes a @classmethod-style property (since @property only works on
    instances).

    ::

        from pytool.lang import classproperty

        class MyClass(object):
            _attr = 'Hello World'

            @classproperty
            def attr(cls):
                return cls._attr

        MyClass.attr # 'Hello World'
        MyClass().attr # Still 'Hello World'

    """
    def __get__(self, instance, owner):
        return func(owner)

    return type(func.__name__, (object,), {
        '__get__':__get__,
        '__module__':func.__module__,
        '__doc__':func.__doc__,
        })()


def singleton(klass):
    """ Wraps a class to create a singleton version of it.

        :param klass: Class to decorate

        Example usage::

            # Make a class directly behave as a singleton
            @singleton
            class Test(object):
                pass

            # Make an imported class behave as a singleton
            Test = singleton(Test)

    """
    cls_dict = {'_singleton': None}

    # Mirror original class
    cls_name = klass.__name__
    for attr in functools.WRAPPER_ASSIGNMENTS:
        cls_dict[attr] = getattr(klass, attr)

    # Make new method that controls singleton behavior
    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = klass(*args, **kwargs)
        return cls._singleton

    # Add new method to singleton class dict
    cls_dict['__new__'] = __new__

    # Build and return new class
    return type(cls_name, (object,), cls_dict)


def hashed_singleton(klass):
    """ Wraps a class to create a hashed singleton version of it. A hashed
        singleton is like a singleton in that there will be only a single
        instance of the class for each call signature.

        The singleton is kept as a `weak reference
        <http://docs.python.org/2/library/weakref.html>`_, so if your program
        ceases to reference the hashed singleton, you may get a new instance if
        the Python interpreter has garbage collected your original instance.

        This will not work for classes that take arguments that are unhashable
        (e.g. dicts, sets).

        :param klass: Class to decorate

        Example usage::

            # Make a class directly behave as a hashed singleton
            @hashed_singleton
            class Test(object):
                def __init__(self, *args, **kwargs):
                    pass

            # Make an imported class behave as a hashed singleton
            Test = hashed_singleton(Test)

            # The same arguments give you the same class instance back
            test = Test('a', k='k')
            test is Test('a', k='k') # True

            # A different argument signature will give you a new instance
            test is Test('b', k='k') # False
            test is Test('a', k='j') # False

            # Removing all references to a hashed singleton instance will allow
            # it to be garbage collected like normal, because it's only kept
            # as a weak reference
            del test
            test = Test('a', k='k') # If the Python interpreter has garbage
                                    # collected, you will get a new instance


    """
    cls_dict = {'_singletons': weakref.WeakValueDictionary()}

    # Mirror original class
    cls_name = klass.__name__
    for attr in functools.WRAPPER_ASSIGNMENTS:
        cls_dict[attr] = getattr(klass, attr)

    # Make new method that controls singleton behavior
    def __new__(cls, *args, **kwargs):
        hashable_kwargs = tuple(sorted(kwargs.iteritems()))
        signature = (args, hashable_kwargs)

        if signature not in cls._singletons:
            obj = klass(*args, **kwargs)
            cls._singletons[signature] = obj
        else:
            obj = cls._singletons[signature]

        return obj

    # Add new method to singleton class dict
    cls_dict['__new__'] = __new__

    # Build and return new class
    return type(cls_name, (object,), cls_dict)


class _UNSETMeta(type):
    def __nonzero__(cls):
        return False

    def __len__(cls):
        return 0

    def __eq__(cls, other):
        if cls is other:
            return True
        if not other:
            return True
        return False

    def __iter__(cls):
        return cls

    def next(cls):
        raise StopIteration()

    def __repr__(cls):
        return 'UNSET'


class UNSET(object):
    """ Special class that evaluates to ``bool(False)``, but can be distinctly
        identified as seperate from ``None`` or ``False``. This class can and
        should be used without instantiation.

        ::

            >>> from pytool.lang import UNSET
            >>> # Evaluates to False
            >>> bool(UNSET)
            False
            >>> # Is a class-singleton (cannot become an instance)
            >>> UNSET() is UNSET
            True
            >>> # Is good for checking default values
            >>> if {}.get('example', UNSET) is UNSET:
            ...     print "Key is missing."
            ...     
            Key is missing.
            >>> # Has no length
            >>> len(UNSET)
            0
            >>> # Is iterable, but has no iterations
            >>> list(UNSET)
            []
            >>> # It has a repr() equal to itself
            >>> UNSET
            UNSET

    """
    __metaclass__ = _UNSETMeta

    def __new__(cls):
        return cls


class Namespace(object):
    """
    Namespace object used for creating arbitrary data spaces. This can be used
    to create nested namespace objects. It can represent itself as a dictionary
    of dot notation keys.

    Example::

        >>> from pytool.lang import Namespace
        >>> # Namespaces automatically nest
        >>> myns = Namespace()
        >>> myns.hello = 'world'
        >>> myns.example.value = True
        >>> # Namespaces can be converted to dictionaries
        >>> myns.as_dict()
        {'hello': 'world', 'example.value': True}
        >>> # Namespaces have container syntax
        >>> 'hello' in myns
        True
        >>> 'example.value' in myns
        True
        >>> 'example.banana' in myns
        False
        >>> 'example' in myns
        True
        >>> # Namespaces are iterable
        >>> for name, value in myns:
        ...     print name, value
        ...     
        hello world
        example.value True

    Namespaces are useful!

    """
    def __init__(self):
        pass

    def __getattr__(self, name):
        # Allow implicit nested namespaces by attribute access
        new_space = Namespace()
        setattr(self, name, new_space)
        return new_space

    def __iter__(self):
        return self.iteritems()

    def __contains__(self, name):
        names = name.split('.')

        obj = self
        for name in names:
            obj = getattr(obj, name)

        if isinstance(obj, Namespace):
            if obj.__dict__:
                return True
            else:
                return False
        else:
            return True

    def iteritems(self, base_name=None):
        """ Return iterator which returns ``(key, value)`` tuples.

            :param str base_name: Base namespace (optional)

        """
        for name, value in self.__dict__.items():
            if base_name:
                name = base_name + '.' + name

            # Allow for nested namespaces
            if isinstance(value, Namespace):
                for subkey in value.iteritems(name):
                    yield subkey
            else:
                yield name, value

    def as_dict(self, base_name=None):
        """ Return the current namespace as a dictionary.

            :param str base_name: Base namespace (optional)

        """
        return dict(self.iteritems(base_name))

    def __repr__(self):
        return "<Namespace({})>".format(self.as_dict())

