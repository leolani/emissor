import enum
import logging
from collections import namedtuple
from dataclasses import is_dataclass

import collections.abc
import marshmallow
import marshmallow_dataclass
import numbers
import numpy as np
import simplejson as json
import sys
import uuid
from marshmallow import fields, EXCLUDE, ValidationError
from numpy.typing import ArrayLike
from rdflib import URIRef
from typing import Any, Callable, TypeVar, Type, Mapping, Union

_logger = logging.getLogger(__name__)


PY_TYPE_FIELD = "_py_type"

Identifier = str


class GenericField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        try:
            object_dict = _marshal(value, cls=value.__class__, serialize=False)
            object_dict[PY_TYPE_FIELD] = f"{value.__class__.__module__}-{value.__class__.__name__}"

            return object_dict
        except Exception:
            return _marshal(value, serialize=False)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            module_, type_ = value[PY_TYPE_FIELD].split("-")
            clazz = getattr(sys.modules[module_], type_)

            return _unmarshal(value, cls=clazz, serialized=False)
        except Exception as e:
            if isinstance(e, ValidationError):
                _logger.warning("Failed to deserialize object (type %s), %s",
                                value[PY_TYPE_FIELD] if PY_TYPE_FIELD in value else "unknown", e.messages)
            return _unmarshal(value, serialized=False)


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


class URIRefField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""

        return value if isinstance(value, str) else value.toPython()

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return URIRef(value) if value != "" else None
        except ValueError as error:
            raise ValidationError("Not an URIRef") from error


class _JsonLdSchema(marshmallow.Schema):
    TYPE_MAPPING: Mapping[Type, fields.Field] = {
        ArrayLike: ArrayLikeField,
        URIRef: URIRefField,
        Any: GenericField,
    }

    """A Schema that marshals data with JSON-LD contexts."""
    _ld_context = fields.Dict(data_key="@context", dump_only=True)
    _ld_type = fields.Str(data_key="@type", dump_only=True)

    class Meta:
        unknown = EXCLUDE


def get_serializable_type_var(name: str, *constraints: type, bound: Union[None, type, str] = None,
                              covariant: bool = False, contravariant: bool = False) -> TypeVar:
    """
    Obtain a :class:`TypeVar` that can be serialized by the :func:`marshal` and :func:`unmarshal`
    functions in this module.

    Parameters
    ----------
    see :class:`TypeVar`

    Returns
    -------
    TypeVar
        A :class:`TypeVar` with the given parameters.
    """
    # noinspection PyTypeHints
    var = TypeVar(name, *constraints, bound=bound, covariant=covariant, contravariant=contravariant)
    _JsonLdSchema.TYPE_MAPPING[var] = GenericField

    return var


def serializer(obj: Any) -> Union[dict, tuple, str, int, float, complex, bool]:
    """
    Convert an object to a type supported by default by :func:`json.dumps`.

    This function can be used as the 'default' parameter in :func:`json.dumps`.

    Parameters
    ----------
    obj : Any
        Object to be serialized.

    Returns
    -------
    Union[dict, tuple, str, int, float, complex, bool]
        The serialized object.
    """
    if isinstance(obj, (str, int, float, complex, bool)):
        return obj
    if isinstance(obj, enum.Enum):
        return obj.name.lower()
    if isinstance(obj, (URIRef, uuid.UUID)):
        return str(obj)
    if isinstance(obj, np.ndarray):
        return tuple(obj.tolist())
    if isinstance(obj, tuple) and hasattr(obj, '_asdict'):
        # noinspection PyProtectedMember
        return obj._asdict()
    if isinstance(obj, collections.abc.Iterable):
        return tuple(obj)

    # Include @property
    attrs = [key for key in dir(obj) if not key.startswith("_") and not callable(getattr(obj, key))]

    return {k: getattr(obj, k) for k in attrs}


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
        The type of the `obj` passed in. If this parameter is used, the object
        should be a dataclass (see :mod:`dataclasses`).
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
    return _marshal(obj, indent=indent, cls=cls, default=default)


def _marshal(obj: Any, *, indent: int = 2, cls: type = None, default: Callable[[Any], Any] = serializer,
            serialize: bool = True) -> str:
    if not cls or not is_dataclass(cls):
        json_string = json.dumps(obj, default=default if default else serializer, indent=indent)
    else:
        is_collection = isinstance(obj, collections.abc.Iterable)
        schema = marshmallow_dataclass.class_schema(cls, base_schema=_JsonLdSchema)()

        json_string = schema.dumps(obj, indent=indent, many=is_collection)

    # noinspection PyProtectedMember
    return json_string if serialize else json.loads(json_string)


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
    return _unmarshal(json_string, cls=cls)


def _unmarshal(json_obj: str, *, cls: type = None, serialized: bool = True) -> Any:
    if cls and is_dataclass(cls):
        mapping = json.loads(json_obj) if serialized else json_obj

        # Valid JSON is either an object, array, number, string, false, null or true (https://tools.ietf.org/rfc/rfc7159.txt)
        if mapping is None or isinstance(mapping, (str, numbers.Number, bool)):
            return mapping

        is_collection = not isinstance(mapping, dict)
        schema = marshmallow_dataclass.class_schema(cls, base_schema=_JsonLdSchema)()

        return schema.load(mapping, unknown=marshmallow.EXCLUDE, many=is_collection)
    elif not serialized:
        if isinstance(json_obj, dict):
            return object_hook(json_obj)
        elif isinstance(json_obj, (list, tuple)):
            return [_unmarshal(item, serialized=False) for item in json_obj]
        else:
            return json_obj
    else:
        return json.loads(json_obj, object_hook=object_hook)


def object_hook(obj_dict):
    valid_attributes = {key: val for key, val in obj_dict.items() if key.isidentifier() and not key.startswith("_")}

    return namedtuple('JSON', valid_attributes.keys())(*valid_attributes.values())
