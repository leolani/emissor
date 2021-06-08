import enum
from collections import namedtuple

import collections.abc
import marshmallow
import marshmallow_dataclass
import numbers
import numpy as np
import simplejson as json
import uuid
from abc import ABC
from marshmallow import fields, EXCLUDE, ValidationError
from numpy.typing import ArrayLike
from rdflib import URIRef
from typing import Any, Callable, TypeVar, Generic

from emissor.representation.ldschema import emissor_dataclass

Identifier = str


class ArrayLikeField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""

        return np.array(value).tolist()

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return np.array(value) if value != "" else None
        except ValueError as error:
            raise ValidationError("Not an ArrayLike") from error


class AnyField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return serializer(value)

    def _deserialize(self, value, attr, data, **kwargs):
        return hook(value)


class _JsonLdSchema(marshmallow.Schema):
    TYPE_MAPPING = {ArrayLike: ArrayLikeField,
                    Any: AnyField}

    """A Schema that marshals data with JSON-LD contexts."""
    _ld_context = fields.Dict(data_key="@context", dump_only=True)
    _ld_type = fields.Str(data_key="@type", dump_only=True)

    class Meta:
        unknown = EXCLUDE


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
    schema = marshmallow_dataclass.class_schema(cls, base_schema=_JsonLdSchema)()

    return schema.dumps(obj, indent=indent, many=is_collection)


def unmarshal(json_string: object, *, cls: type = None) -> object:
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
    if cls:
        mapping = json.loads(json_string)

        # Valid JSON is either an object, array, number, string, false, null or true (https://tools.ietf.org/rfc/rfc7159.txt)
        if mapping is None or isinstance(mapping, (str, numbers.Number, bool)):
            return mapping

        is_collection = not isinstance(mapping, dict)
        schema = marshmallow_dataclass.class_schema(cls, base_schema=_JsonLdSchema)()

        return schema.load(mapping, unknown=marshmallow.EXCLUDE, many=is_collection)
    else:
        return json.loads(json_string, object_hook=hook)


def hook(obj_dict):
    valid_attributes = {k: v for k, v in obj_dict.items() if k.isidentifier()}

    return namedtuple('JSON', valid_attributes.keys())(*valid_attributes.values())


if __name__ == '__main__':
    @emissor_dataclass
    class Ruler(ABC):
        container_id: Identifier

    @emissor_dataclass
    class TemporalRuler(Ruler):
        start: int
        end: int


    R = TypeVar('R', bound=Ruler)
    T = TypeVar('T')

    @emissor_dataclass
    class Container(Generic[R, T], ABC):
        pass


    @emissor_dataclass
    class BaseContainer(Container[R, T], ABC):
        id: Identifier
        ruler: R


    @emissor_dataclass
    class TemporalContainer(BaseContainer[TemporalRuler, TemporalRuler]):
        ruler: TemporalRuler

    t = TemporalContainer("cid", TemporalRuler("rid", 0, 1))
    print(t._ld_context)
    print(marshal(t, cls=TemporalContainer))
    s = marshal(t, cls=TemporalContainer)
    print(unmarshal(s, cls=TemporalContainer))
    tr = TemporalRuler("rid", 0, 1)
    print(marshal(tr, cls=TemporalRuler))
    print(unmarshal(marshal(tr, cls=TemporalRuler), cls=TemporalRuler))
