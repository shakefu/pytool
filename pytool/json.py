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
except ImportError:
    # Hack around relative imports allowing a module to import itself
    import importlib
    json = importlib.import_module('json')


# Conditionally handle bson import so we don't have to depend on pymongo
try:
    import bson
except ImportError:
    # Make a mock bson module (as a class object)
    bson = type('bson', (object,),
            {'ObjectId': type('ObjectId', (object,), {})})


__all__ = [
        'as_json',
        'from_json',
]

def as_json(obj):
    """ Returns an object JSON encoded properly.

        Adds additional encoders for :class:`~datetime.datetiem` and
        :class:`bson.ObjectId`.

        :param object obj: An object to encode.
        :returns: JSON encoded version of *obj*.

    """
    def encode(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%a %b %d %Y %H:%M:%S %z')
        elif isinstance(obj, bson.ObjectId):
            return str(obj)
        return json.JSONEncoder.default(encoder, obj)

    encoder = json.JSONEncoder(default=encode)
    return encoder.encode(obj)


def from_json(value):
    """ Decodes a JSON string into an object.

        :param str value: String to decode
        :returns: Decoded JSON object

    """
    return json.loads(value)


