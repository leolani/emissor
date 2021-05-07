import collections.abc
import enum
import numbers
import uuid
from collections import namedtuple
from typing import Optional, Any, Callable

import marshmallow
import marshmallow_dataclass
import numpy as np
import simplejson as json
from rdflib import URIRef

Identifier = Optional[str]


class Typed:
    @property
    def type(self) -> str:
        return self.__class__.__name__


def serializer(obj):
    if isinstance(obj, enum.Enum):
        return obj.name.lower()
    if isinstance(obj, (URIRef, uuid.UUID)):
        return str(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, tuple) and hasattr(obj, '_asdict'):
        return obj._asdict()
    if isinstance(obj, collections.abc.Iterable):
        return list(obj)

    # Include @property
    fields = [key for key in dir(obj) if not key.startswith("_") and not callable(getattr(obj, key))]

    return {k: getattr(obj, k) for k in fields}


def marshal(obj: Any, *, indent: int = 2, cls: type = None, default: Callable[[Any], Any] = serializer) -> str:
    """Serialize a Python object to JSON.

    Serialization can be performed either based on the type of the object, in
    which case the `cls` parameter must be provided, or using a conversion
    function to default types, provided by the `default` parameter.

    Parameters
    ----------
    obj : Any
        The object to be serialized.
    indent : int, optional, default: '2'
        Formatting parameter for the returned JSON string.
    cls : type, optional
        The type of the `obj` passed in. If this parameter is used, the object should be
         a dataclass (see :mod:`dataclasses).
        If `cls` is not 'None', `default` is ignored.
    default : Callable[[Any], Any], optional, default: :func:`serializer`
        A function that converts any object to a Python type that is supported
        by :mod:`json` by default, i.e. one of primitive type, list, dict.
        If `cls` is not 'None', `default` is ignored.

    Returns
    -------
    str
        The serialized JSON object.
    """
    if not cls:
        return json.dumps(obj, default=default if default else serializer, indent=indent)

    is_collection = isinstance(obj, collections.abc.Iterable)
    schema = marshmallow_dataclass.class_schema(cls)()

    return schema.dumps(obj, indent=indent, many=is_collection)


def unmarshal(json_string: str, *, cls: type = None) -> Any:
    """Deserialize a JSON to a Python object.

    Deserialization can be performed either based on the expected output type,
    in which case the `cls` parameter must be provided, or to a named tuple.

    Parameters
    ----------
    json_string : str
        The object to be serialized.
    cls : type, optional
        The type of the expected output. If this parameter is used, its value
        should be a dataclass (see :mod:`dataclasses).
        If the input is a collection, the expected type of its elements should
        be provided.

    Returns
    -------
    object
        The deserialized form of the provided JSON object. If `cls` is provided,
        an instance or collection of this type is returned, otherwise a named
        tuple.
    """
    if not cls:
        return json.loads(json_string, object_hook=lambda d: namedtuple('JSON', d.keys())(*d.values()))

    mapping = json.loads(json_string)

    # Valid JSON is either an object, array, number, string, false, null or true (https://tools.ietf.org/rfc/rfc7159.txt)
    if mapping is None or isinstance(mapping, (str, numbers.Number, bool)):
        return mapping

    is_collection = not isinstance(mapping, dict)
    schema = marshmallow_dataclass.class_schema(cls)()

    return schema.load(mapping, unknown=marshmallow.EXCLUDE, many=is_collection)
