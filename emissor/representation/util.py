import collections.abc
import enum
import numbers
import uuid
from collections import namedtuple
from typing import Optional, Any

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


def marshal(obj: Any, *, indent: int = 2, cls: type = None, default=None) -> str:
    if not cls:
        return json.dumps(obj, default=default if default else serializer, indent=indent)

    if default:
        raise ValueError("don't specify default if cls is already specified")

    is_collection = isinstance(obj, collections.abc.Iterable)
    schema = marshmallow_dataclass.class_schema(cls)()

    return schema.dumps(obj, indent=indent, many=is_collection)


def unmarshal(json_string: str, *, cls: type = None) -> Any:
    if not cls:
        return json.loads(json_string, object_hook=lambda d: namedtuple('JSON', d.keys())(*d.values()))

    mapping = json.loads(json_string)

    # Valid JSON is either an object, array, number, string, false, null or true (https://tools.ietf.org/rfc/rfc7159.txt)
    if mapping is None or isinstance(mapping, (str, numbers.Number, bool)):
        return mapping

    is_collection = not isinstance(mapping, dict)
    schema = marshmallow_dataclass.class_schema(cls)()

    return schema.load(mapping, unknown=marshmallow.EXCLUDE, many=is_collection)
