import enum
from collections import namedtuple, Iterable
from dataclasses import dataclass

import numpy as np
import simplejson as json
import uuid
from rdflib import URIRef
from typing import Optional, Any, Union
import marshmallow_dataclass


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
    if isinstance(obj, Iterable):
        return list(obj)

    # Include @property
    fields = [key for key in dir(obj) if not key.startswith("_") and not callable(getattr(obj, key))]

    return {k: getattr(obj, k) for k in fields}


def marshal(obj: Any, indent: int=None) -> str:
    schema = marshmallow_dataclass.class_schema(obj.__class__)()

    return json.dumps(schema.dump(obj), indent=indent)


def unmarshal(json_string: str, cls: type=None) -> Any:
    if cls:
        schema = marshmallow_dataclass.class_schema(cls)()
        return schema.loads(json_string)

    return json.loads(json_string, object_hook=lambda d: namedtuple('JSON', d.keys())(*d.values()))
