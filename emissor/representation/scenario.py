import enum
import uuid
from abc import ABC
from typing import Iterable, Dict, TypeVar, Type, Generic, List, Optional

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
