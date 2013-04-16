"""
This module contains helpers for working with JSON data.

Tries to use the `simplejson` module if it exists, otherwise falls back to the
`json` module.

If the `bson` module exists, it allows `bson.ObjectId` objects to be decoded
into JSON automatically.

"""
from datetime import datetime

try:
    import simplejson as json
    _simplejson = True
except ImportError:
    # Hack around relative imports allowing a module to import itself
    import importlib
    json = importlib.import_module('json')
    _simplejson = False


# Conditionally handle bson import so we don't have to depend on pymongo
try:
    import bson
except ImportError:
    # Make a mock bson module (as a class object)
    bson = type('bson', (object,),
            {'ObjectId': type('ObjectId', (object,), {})})

import pytool


__all__ = [
        'as_json',
        'from_json',
]


class _JSONEncoder(json.JSONEncoder):
    """ This subclasses JSONEncoder to implement the ``for_json()`` hook even
        for types that are recognized by the default JSONEncoder (i.e. dict
        subclasses).

    """
    def encode(self, obj):
        """ Encode an object as a JSON string. """
        # Look for the for_json() hook to help things along
        for_json = getattr(obj, 'for_json', None)
        if for_json and callable(for_json):
            obj = for_json()
        # Encode our object
        return json.JSONEncoder.encode(self, obj)

    def default(self, obj):
        """ Handle encoding of an object which isn't JSON serializable by the
        regular encoder. """
        # Look for the for_json() hook before anything else
        for_json = getattr(obj, 'for_json', None)
        if for_json and callable(for_json):
            return for_json()
        # Datetime objects get encoded according to the ISO standard
        if isinstance(obj, datetime):
            return obj.strftime('%a %b %d %Y %H:%M:%S %z').strip()
        # BSON ObjectId types get encoded as their hex string
        if isinstance(obj, bson.ObjectId):
            return str(obj)
        # Attempt to encode objects which have an _asdict method if we're not
        # using simplejson. We don't do this with simplejson, because their C
        # speedups call _asdict directly so we don't have to.
        if not _simplejson:
            # If it's not simplejson, we do _asdict behavior handling ourselves
            _asdict = getattr(obj, '_asdict', None)
            if _asdict and callable(_asdict):
                return _asdict()
        # This will raise a TypeError, which is what we want at this point
        return json.JSONEncoder.default(self, obj)


def as_json(obj, **kwargs):
    """
    Returns an object JSON encoded properly.

    This method allows you to implement a hook method ``for_json()`` on your
    objects if you want to allow arbitrary objects to be encoded to JSON. A
    ``for_json()`` hook must return a basic JSON type (dict, list, int, float,
    string, unicode, float or None), or a basic JSON type which contains other
    objects which implement the ``for_json()`` hook.

    If an object implements both ``_asdict()`` and ``for_json()`` the latter is
    given preference.

    Also adds additional encoders for :class:`~datetime.datetime` and
    :class:`bson.ObjectId`.

    :param object obj: An object to encode.
    :param \*\*kwargs: Any optional keyword arguments to pass to the \
                       JSONEncoder
    :returns: JSON encoded version of `obj`.

    .. versionadded:: 2.4
       Objects which have an ``_asdict()`` method will have that method
       called as part of encoding to JSON, even when not using simplejson.

    .. versionadded:: 2.4
       Objects which have a ``for_json()`` method will have that method called
       and the return value used for encoding instead.

    """
    return _JSONEncoder().encode(obj)


def from_json(value):
    """ Decodes a JSON string into an object.

        :param str value: String to decode
        :returns: Decoded JSON object

    """
    return json.loads(value)


