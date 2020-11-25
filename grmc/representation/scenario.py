# Define Annotation Class
import dataclasses
import enum
import inspect
import os
from abc import ABC
from dataclasses import dataclass

import json
import uuid
from typing import Iterable, Dict, TypeVar, Type, Generic, Any, List

from grmc.representation.container import Container, TemporalContainer, Ruler, TemporalRuler, Sequence, \
    ArrayContainer, Index, MultiIndex
from grmc.representation.entity import Person, Object
from grmc.representation.util import Identifier, serializer, Typed

T = TypeVar('T')
U = TypeVar('U')


class Modality(enum.Enum):
    IMAGE = 0
    TEXT = 1
    AUDIO = 2
    VIDEO = 3


@dataclass
class Annotation(Generic[T], Typed):
    value: T
    source: Identifier
    timestamp: int

    @property
    def type(self) -> str:
        return self.value.__class__.__name__


@dataclass
class Mention:
    segment: List[Ruler]
    annotations: List[Annotation[Any]]


R = TypeVar('R', bound=Ruler)
@dataclass
class Signal(Container[R, T], ABC):
    modality: Modality
    time: TemporalRuler
    files: List[str]
    mentions: List[Mention]


@dataclass
class TextSignal(Signal[Sequence, str], Sequence[str]):
    @classmethod
    def for_scenario(cls: Type[U], scenario_id: Identifier, start: int, stop: int, file: str, text: str = None,
                     mentions: Iterable[Mention] = None) -> U:
        return cls(uuid.uuid4(), Index.from_range(start, stop), start, stop, tuple(text) if text else text,
                   Modality.TEXT.name.lower(), TemporalRuler(scenario_id, start, stop), [file], list(mentions) if mentions else [])


@dataclass
class ImageSignal(Signal[ArrayContainer, float], ArrayContainer[float]):
    @classmethod
    def for_scenario(cls: Type[U], scenario_id: Identifier, start: int, stop: int, file: str,
                     bounds: Iterable[int], mentions: Iterable[Mention] = None) -> U:
        return cls(uuid.uuid4(), MultiIndex(None, bounds), None, Modality.IMAGE.name.lower(),
                   TemporalRuler(scenario_id, start, stop), [file], list(mentions) if mentions else [])


@dataclass
class AudioSignal(Signal[ArrayContainer, float], ArrayContainer[float]):
    # TODO factory
    pass


@dataclass
class VideoSignal(Signal[ArrayContainer, float], ArrayContainer[float]):
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
    print(json.dumps(Annotation("test", "text", 123), default=serializer))