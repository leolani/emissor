# Define Annotation Class
import enum
import os
from abc import ABC
from dataclasses import dataclass

import json
import uuid
import numpy as np
from typing import Iterable, Dict, TypeVar, Type, Generic, Any, List

from emissor.representation.container import Container, TemporalContainer, Ruler, TemporalRuler, Sequence, \
    ArrayContainer, Index, MultiIndex, BaseContainer
from emissor.representation.entity import Person, Object
from emissor.representation.util import Identifier, serializer, Typed

T = TypeVar('T')
U = TypeVar('U')


class Modality(enum.Enum):
    IMAGE = 0
    TEXT = 1
    AUDIO = 2
    VIDEO = 3


@dataclass
class Annotation(Generic[T]):
    type: str
    value: T
    source: Identifier
    timestamp: int


@dataclass
class Mention:
    id: Identifier
    segment: List[Ruler]
    annotations: List[Annotation[Any]]


R = TypeVar('R', bound=Ruler)
@dataclass
class Signal(BaseContainer[R, T], ABC):
    modality: Modality
    time: TemporalRuler
    files: List[str]
    mentions: List[Mention]


@dataclass
class TextSignal(Signal[Index, str], Sequence[str]):
    @classmethod
    def for_scenario(cls: Type[U], scenario_id: Identifier, start: int, stop: int, file: str, text: str = None,
                     mentions: Iterable[Mention] = None) -> U:
        return cls(str(uuid.uuid4()), Index.from_range(start, stop), start, stop, tuple(text) if text else text,
                   Modality.TEXT, TemporalRuler(scenario_id, start, stop), [file], list(mentions) if mentions else [])


@dataclass
class ImageSignal(Signal[MultiIndex, np.array], ArrayContainer):
    @classmethod
    def for_scenario(cls: Type[U], scenario_id: Identifier, start: int, stop: int, file: str,
                     bounds: Iterable[int], mentions: Iterable[Mention] = None) -> U:
        return cls(str(uuid.uuid4()), MultiIndex(None, tuple(bounds)), None, Modality.IMAGE,
                   TemporalRuler(scenario_id, start, stop), [file], list(mentions) if mentions else [])


@dataclass
class AudioSignal(Signal[MultiIndex, np.array], ArrayContainer):
    # TODO factory
    pass


@dataclass
class VideoSignal(Signal[MultiIndex, np.array], ArrayContainer):
    # TODO factory
    pass


@dataclass
class ScenarioContext:
    agent: Identifier
    speaker: Person
    persons: List[Person]
    objects: List[Object]


@dataclass
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