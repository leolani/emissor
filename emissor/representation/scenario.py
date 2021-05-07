import enum
import json
import os
import uuid
from abc import ABC
from typing import Iterable, Dict, TypeVar, Type, Generic, Any, List

import numpy as np

from emissor.representation.container import TemporalContainer, Ruler, TemporalRuler, Sequence, \
    ArrayContainer, Index, MultiIndex, BaseContainer
from emissor.representation.entity import Person, Object
from emissor.representation.ldschema import emissor_dataclass
from emissor.representation.util import Identifier, serializer

T = TypeVar('T')
U = TypeVar('U')


class Modality(enum.Enum):
    IMAGE = 0
    TEXT = 1
    AUDIO = 2
    VIDEO = 3


@emissor_dataclass
class Annotation(Generic[T]):
    type: str
    value: T
    source: Identifier
    timestamp: int


@emissor_dataclass
class Mention:
    id: Identifier
    segment: List[Ruler]
    annotations: List[Annotation[Any]]


R = TypeVar('R', bound=Ruler)


@emissor_dataclass
class Signal(BaseContainer[R, T], ABC):
    modality: Modality
    time: TemporalRuler
    files: List[str]
    mentions: List[Mention]


@emissor_dataclass
class TextSignal(Signal[Index, str], Sequence[str]):
    @classmethod
    def for_scenario(cls: Type[U], scenario_id: Identifier, start: int, stop: int, file: str, text: str = None,
                     mentions: Iterable[Mention] = None) -> U:
        return cls(str(uuid.uuid4()), Index.from_range(start, stop), start, stop, tuple(text) if text else text,
                   Modality.TEXT, TemporalRuler(scenario_id, start, stop), [file], list(mentions) if mentions else [])


@emissor_dataclass
class ImageSignal(Signal[MultiIndex, np.array], ArrayContainer):
    @classmethod
    def for_scenario(cls: Type[U], scenario_id: Identifier, start: int, stop: int, file: str,
                     bounds: Iterable[int], mentions: Iterable[Mention] = None) -> U:
        return cls(str(uuid.uuid4()), MultiIndex(None, tuple(bounds)), None, Modality.IMAGE,
                   TemporalRuler(scenario_id, start, stop), [file], list(mentions) if mentions else [])


@emissor_dataclass
class AudioSignal(Signal[MultiIndex, np.array], ArrayContainer):
    # TODO factory
    pass


@emissor_dataclass
class VideoSignal(Signal[MultiIndex, np.array], ArrayContainer):
    # TODO factory
    pass


@emissor_dataclass
class ScenarioContext:
    agent: Identifier
    speaker: Person
    persons: List[Person]
    objects: List[Object]


@emissor_dataclass
class Scenario(TemporalContainer):
    context: ScenarioContext
    signals: Dict[str, str]

    @classmethod
    def new_instance(cls: Type[U], scenario_id: str, start: int, end: int, context: ScenarioContext,
                     signals: Dict[str, str]) -> U:
        temporal_ruler = TemporalRuler(None, start, end)
        return cls(scenario_id, temporal_ruler, context, signals)


# TODO Just a list or with some structure, e.g. relate the ruler in the file (dict: time -> event)
def append_signal(path: str, signal: object, terminate: bool = False, indent: int = 4):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    initialize = not os.path.isfile(path)
    with open(path, "a") as signal_file:
        if initialize:
            signal_file.write("[\n")
        if signal:
            json.dump(signal, signal_file, default=serializer, indent=indent)
            signal_file.write(",\n")
        if terminate:
            signal_file.write("]")


if __name__ == "__main__":
    print(json.dumps(Annotation("str", "test", "text", 123), default=serializer))