import enum
from collections import namedtuple, Iterable

import numpy as np
# import json
import simplejson as json
import uuid
from rdflib import URIRef
from typing import Optional, Any

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


def marshal(obj: Any) -> str:
    return json.dumps(obj, default=serializer, indent=2)


def unmarshal(json_string: str) -> Any:
    return json.loads(json_string, object_hook=lambda d: namedtuple('JSON', d.keys())(*d.values()))
