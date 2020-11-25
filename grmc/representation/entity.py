# Define Annotation Class
import enum
from dataclasses import dataclass

from grmc.representation.util import Identifier


class Emotion(enum.Enum):
    NEUTRAL = 0
    ANGER = 1
    DISGUST = 2
    FEAR = 3
    HAPPINESS = 4
    JOY = 5
    SADNESS = 6
    SURPRISE = 7


class Gender(enum.Enum):
    UNDEFINED = 0
    FEMALE = 1
    MALE = 2
    OTHER = 3


@dataclass
class Instance:
    id: Identifier


@dataclass
class Object(Instance):
    label: str


@dataclass
class Person(Instance):
    name: str
    age: int
    gender: Gender


@dataclass
class Friend(Person):
    pass
