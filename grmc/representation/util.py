import enum
from collections import namedtuple
from types import SimpleNamespace

# import json
import simplejson as json

import numpy as np
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

    # Include @property
    keys = [k for k in dir(obj) if not k.startswith("_")]

    return {k: getattr(obj, k) for k in keys if not callable(getattr(obj, k))}


def marshal(obj: Any) -> str:
    return json.dumps(obj, default=serializer, indent=2)


def unmarshal(json_string: str) -> Any:
    return json.loads(json_string, object_hook=lambda d: namedtuple('JSON', d.keys())(*d.values()))