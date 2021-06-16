from dataclasses import dataclass, field, Field

import inspect
from rdflib import URIRef, Namespace
from typing import Union, IO, Any, Optional, Mapping, ClassVar, Tuple, Type

LD_CONTEXT_FIELD = "_ld_context"
LD_TYPE_FIELD = "_ld_type"

EMISSOR_NAMESPACE = "https://emissor.org"


def emissor_dataclass(cls: Type = None, **kwargs):
    def wrapper(clazz):
        ld_type_kw = _get_kw_args(ld_type)
        ld_type_args = {k: v for k, v in kwargs.items() if k in ld_type_kw}
        if not "namespace" in ld_type_args:
            ld_type_args["namespace"] = EMISSOR_NAMESPACE
        ld_clazz = ld_type(**ld_type_args)(clazz)

        dataclass_kw = _get_kw_args(dataclass)
        dataclass_args = {k: v for k, v in kwargs.items() if k in dataclass_kw}

        return dataclass(ld_clazz, **dataclass_args)

    return wrapper(cls) if cls else wrapper


@dataclass
class LdProperty:
    """
    Adds linked data information to an attribute of the dataclass.
    """
    val: Optional[Any] = field(default_factory=lambda: field())
    prefix: Optional[str] = None
    alias: Optional[str] = None
    type: Optional[str] = None
    ignore: bool = False


@dataclass
class LdId(LdProperty):
    """
    Adds linked data information to an attribute of the dataclass where the
    value is an identifier in the linked data model.
    """
    type: str = "@id"


def ld_type(*, namespace: Union[URIRef, str] = None, type_name: str = None, separator: str = "#",
            prefixes: Mapping[str, str] = None, ontology: Union[str, IO] = None) -> Type:
    """
    Decorator to add linked data information to a dataclass.

    The decorator must be used after the dataclass decorator:
        @dataclass
        @ld_type
        class MyClass:
            ...

    URIs are resolved as follows:

    `namespace` is used as the base URI or prefix. If it is present, and doesn't end with a '/' or '#',
    it is assumed to be a base URL and `separator` is used to resolve names. Else, names are appended.

    Examples:
        namespace="http://schema.org", type_name="Person" resolves to "http://schema.org#Person"
        namespace="http://schema.org", type_name="Person", separator="/" resolves to "http://schema.org/Person"
        namespace="http://schema.org/", type_name="Person" resolves to "http://schema.org/Person"

    Parameters
    ----------
    namespace : Union[URIRef, str]
        The base namespace to be used for type and relation URIs.
    type_name : str, default: None
        The type name. If 'None', the class name is used.
    separator : str, default: '#'
        The separator to use between the base URI and the entity name.
    prefixes: Mapping[str, str], default: None
    ontology :
        Not yet supported

    Returns
    -------
    Type
        Python class object with the added linked data information.
    """
    if ontology:
        raise NotImplementedError("ontology not yet supported")
        # load_ontology
        # load relation names from ontology
        # load relation domains from ontology
        # match names with annotations and fields
        # resolve property names to URI

    ns = _to_namespace(namespace, separator)

    def type_wrapper(cls):
        type_ = type_name if type_name else cls.__name__

        context = {type_: resolve_ref(type_, ns, None), "id": "@id"}
        for clazz in cls.mro():
            context = {**context, **extract_context(clazz)}

        # add annotations to the current (sub-)class definition as dataclasses look them up here
        class_annotations = getattr(cls, "__annotations__", {})
        class_annotations[LD_CONTEXT_FIELD] = ClassVar[dict]
        class_annotations[LD_TYPE_FIELD] = ClassVar[str]
        cls.__annotations__ = class_annotations

        setattr(cls, LD_CONTEXT_FIELD, context)
        setattr(cls, LD_TYPE_FIELD, type_)

        return cls

    def extract_context(cls):
        if '_ld_context' in cls.__dict__:
            return {k: v for k, v in cls._ld_context.items() if k in cls.__annotations__}

        if not hasattr(cls, '__annotations__'):
            return {}

        attributes = {attribute_name: getattr(cls, attribute_name, None)
                      for attribute_name in cls.__annotations__
                      if valid_name(attribute_name)}

        for attribute_name, annotation in filter(is_ld_property, attributes.items()):
            setattr(cls, attribute_name, annotation.val)

        return {attr_name: resolve_ref(attr_name, ns, annotation)
                for attr_name, annotation in attributes.items()
                if not attr_name == "id"}

    def valid_name(attr_name):
        return attr_name[0].isalpha()

    def resolve_ref(ref_name,
                    ref_ns: Namespace = None,
                    val: Any = None) -> Tuple[str, Union[URIRef, Mapping[str, Union[str, URIRef]]]]:
        if not isinstance(val, LdProperty):
            return URIRef(ref_ns[ref_name])

        alias = val.alias if val.alias is not None else ref_name
        if val.prefix == "":
            property_ref = alias
        elif not val.prefix:
            property_ref = ref_ns[alias]
        else:
            prefix = _to_namespace(val.prefix, separator)
            property_ref = prefix[alias]

        # TODO validate type: if ':' in type assert prefix in prefixes
        return {"@id": property_ref, "@type": val.type} if val.type else property_ref

    def is_ld_property(attribute_item):
        _, val = attribute_item
        return isinstance(val, LdProperty)

    return type_wrapper


def _to_namespace(namespace, separator):
    return Namespace(namespace if str(namespace).endswith(("/", "#")) else namespace + separator)


def _get_kw_args(f):
    signature = inspect.signature(f)

    return tuple(signature.parameters.keys())
