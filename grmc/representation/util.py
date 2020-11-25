import enum

import numpy as np
import uuid
from rdflib import URIRef
from typing import Union

Identifier = Union[URIRef, uuid.UUID, str, None]


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

    # Include @property
    keys = [k for k in dir(obj) if not k.startswith("_")]

    return {k: getattr(obj, k) for k in keys if not callable(getattr(obj, k))}