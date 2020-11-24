# Define Annotation Class
import enum
import os
from dataclasses import dataclass

import json
import uuid
from typing import Iterable, Union, Dict, Tuple, TypeVar

from grmc.representation.container import Container, TemporalContainer, Ruler, TemporalRuler, Sequence, ArrayContainer
from grmc.representation.entity import Person, Object
from grmc.representation.util import Identifier, serializer


class Modality(enum.Enum):
    IMAGE = 0
    TEXT = 1
    AUDIO = 2
    VIDEO = 3


@dataclass
class Annotation:
    value: object
    source: Identifier
    timestamp: int

    @property
    def type(self):
        return value.__class__.__name__

@dataclass
class Mention:
    segment: Iterable[Ruler]
    annotations: Iterable[Annotation]


R = TypeVar('R', bound=Ruler)
T = TypeVar('T')
@dataclass
class Signal(Container[R, T]):
    modality: Modality
    time: TemporalRuler
    files: Iterable[str]
    mentions: Iterable[Mention]


@dataclass
class TextSignal(Signal[Sequence, str], Sequence[str]):
    pass


@dataclass
class ImageSignal(Signal[ArrayContainer, float], ArrayContainer[float]):
    pass


@dataclass
class AudioSignal(Signal[ArrayContainer, float], ArrayContainer[float]):
    pass


@dataclass
class VideoSignal(Signal[ArrayContainer, float], ArrayContainer[float]):
    pass

@dataclass
class ScenarioContext:
    agent: Identifier
    speaker: Person
    persons: Iterable[Person]
    objects: Iterable[Object]

@dataclass
class Scenario(TemporalContainer):
    identifier: Identifier
    start: int
    end: int
    context: ScenarioContext
    signals: Dict[Modality, str]


# TODO Just a list or with some structure, e.g. relate the ruler in the file (dict: time -> event)
def append_signal(path: str, signal: object, terminate: bool=False, indent=4):
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
