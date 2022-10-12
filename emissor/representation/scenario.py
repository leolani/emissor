import enum
import uuid
from abc import ABC
from typing import Iterable, Dict, TypeVar, Type, Generic, List, Optional, Union, Any

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Requires Python >= 3.8.
    pass

from marshmallow import fields
from numpy.typing import ArrayLike

from emissor.representation.container import TemporalContainer, Ruler, TemporalRuler, ArrayContainer, Index, MultiIndex, \
    BaseContainer, Sequence
from emissor.representation.ldschema import emissor_dataclass
from emissor.representation.util import Identifier, marshal, get_serializable_type_var

C = TypeVar('C')
T = get_serializable_type_var('T')
R = get_serializable_type_var('R', bound=Ruler)


class Modality(enum.Enum):
    IMAGE = 0
    TEXT = 1
    AUDIO = 2
    VIDEO = 3


@emissor_dataclass
class Annotation(Generic[T]):
    type: Identifier
    value: T
    source: Identifier
    timestamp: int


@emissor_dataclass
class Mention:
    id: Identifier
    segment: List[T]
    annotations: List[T]


@emissor_dataclass
class Signal(Generic[R, T], BaseContainer[R, T], ABC):
    modality: Modality
    time: TemporalRuler
    files: List[str]
    mentions: List[Mention]


@emissor_dataclass
class TextSignal(Signal[Index, str], Sequence[str]):
    text: str

    @classmethod
    def for_scenario(cls: Type[C], scenario_id: Identifier, start: int, stop: int, file: str, text: str = None,
                     mentions: Iterable[Mention] = None, signal_id: Optional[str] = None) -> C:
        signal_id = signal_id if signal_id else str(uuid.uuid4())
        text = text if text else ""

        return cls(signal_id, Index.from_range(signal_id, 0, len(text)), list(text), Modality.TEXT,
                   TemporalRuler(scenario_id, start, stop), [file] if file else [], list(mentions) if mentions else [],
                   text)


@emissor_dataclass
class ImageSignal(Signal[MultiIndex, ArrayLike], ArrayContainer):
    @classmethod
    def for_scenario(cls: Type[C], scenario_id: Identifier, start: int, stop: int, file: str,
                     bounds: Iterable[int], mentions: Iterable[Mention] = None, signal_id: Optional[str] = None) -> C:
        signal_id = signal_id if signal_id else str(uuid.uuid4())
        return cls(signal_id, MultiIndex(signal_id, tuple(bounds)), None, Modality.IMAGE,
                   TemporalRuler(scenario_id, start, stop), [file] if file else [], list(mentions) if mentions else [])


@emissor_dataclass
class AudioSignal(Signal[MultiIndex, ArrayLike], ArrayContainer):
    @classmethod
    def for_scenario(cls: Type[C], scenario_id: Identifier, start: int, stop: int, file: str,
                     length: int, channels: int, mentions: Iterable[Mention] = None, signal_id: Optional[str] = None) -> C:
        signal_id = signal_id if signal_id else str(uuid.uuid4())
        return cls(signal_id, MultiIndex(signal_id, (0, 0, length, channels)), None, Modality.AUDIO,
                   TemporalRuler(scenario_id, start, stop), [file] if file else [], list(mentions) if mentions else [])


@emissor_dataclass
class VideoSignal(Signal[MultiIndex, ArrayLike], ArrayContainer):
    # TODO factory
    pass


@emissor_dataclass
class ScenarioContext(ABC):
    agent: Identifier


SC = get_serializable_type_var("SC", bound=ScenarioContext)


@emissor_dataclass
class Scenario(TemporalContainer, Generic[SC]):
    context: SC
    signals: Dict[str, str]

    @classmethod
    def new_instance(cls: Type[C], scenario_id: str, start: int, end: int, context: ScenarioContext,
                     signals: Dict[str, str]) -> C:
        temporal_ruler = TemporalRuler(scenario_id, start, end)
        return cls(scenario_id, temporal_ruler, context, signals)


class AnnotationField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return marshal(value, cls=value.__class__)

    def _deserialize(self, value, attr, data, **kwargs):
        return None


def class_source(cls: Union[type, Any], include_type: bool = False) -> Identifier:
    """
    Provides a common representation of a class that can be used to identify
    the source of an annotation.

    Requires Python 3.8.

    Example
    -------
    Call the function with an object instance or type::

        annotation_source = class_source(obj)
        annotation_source = class_source(obj.__class__)
        annotation_source = class_source(MyClass)

    Parameters
    ----------
    cls: Union[type, Any]
        The object type or object instance that is the source of an annotation.
    include_type: bool
        Include the class name in the representation. If False, the
        representation is created only from the module that contains the class.
        By default, the type is not included.

    Returns
    -------
    Identifier
        An identifier representing the class that can be used as source of an annotation.
    """
    clazz = cls if type(cls) == type else cls.__class__
    source_module = module_source(clazz.__module__)

    if not include_type:
        return source_module

    # Split into module name and version
    parts = source_module.split("#")
    parts[0] += "." + clazz.__qualname__

    return "#".join(parts)


def module_source(module_name) -> Identifier:
    """
    Provides a common representation of a module name that can be used to identify
    the source of an annotation.

    Requires Python 3.8.

    Example
    -------
    Call the function with the current module name::

        annotation_source = module_source(__name__)

    Parameters
    ----------
    module_name: str
        The name of the module that is the source of an annotation. The name of
        the current module can be retrieved from the global `__name__` variable
        at the place where this function is called.

    Returns
    -------
    Identifier
        An identifier representing a module that can be used to identify the source of an annotation.
    """
    try:
        source = module_name + "#" + version(module_name)
    except PackageNotFoundError:
        source = module_name

    return "python-source:" + source


def class_type(cls) -> Identifier:
    """
    Provides a common representation of a class name that can be used to
    identify the type of an annotation.

    Requires Python 3.8.

    Example
    -------
    Call the function with an object instance or type::

        annotation_type = class_type(obj)
        annotation_type = class_type(obj.__class__)
        annotation_type = class_type(MyValueClass)

    Parameters
    ----------
    cls: Union[type, Any]
        The object type or object instance of an annotation value that should
        be represented.

    Returns
    -------
    Identifier
        An identifier representing a module that can be used to identify the
        source of an annotation.
    """
    clazz = cls if isinstance(cls, type) else cls.__class__

    return "python-type:" + ".".join([clazz.__module__, clazz.__qualname__])
