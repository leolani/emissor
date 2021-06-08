# Define Annotation Class
import enum

from emissor.representation.ldschema import emissor_dataclass
from emissor.representation.util import Identifier


class Emotion(enum.Enum):
    NEUTRAL = 0
    ANGER = 1
    DISGUST = 2
    FEAR = 3
    JOY = 4
    SADNESS = 5
    SURPRISE = 6


class Gender(enum.Enum):
    UNDEFINED = 0
    FEMALE = 1
    MALE = 2
    OTHER = 3


@emissor_dataclass
class Instance:
    id: Identifier


@emissor_dataclass
class Object(Instance):
    label: str


@emissor_dataclass
class Person(Instance):
    name: str
    age: int
    gender: str


@emissor_dataclass
class Friend(Person):
    pass
