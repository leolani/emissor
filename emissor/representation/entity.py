# Define Annotation Class

"""Leolani specific data"""

import enum

from typing import List

from emissor.representation.ldschema import emissor_dataclass
from emissor.representation.scenario import ScenarioContext
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


@emissor_dataclass(namespace="http://cltl.nl/leolani/n2mu")
class Object(Instance):
    label: str


@emissor_dataclass(namespace="http://cltl.nl/leolani/n2mu")
class Person(Instance):
    name: str
    age: int
    gender: Gender


@emissor_dataclass(namespace="http://cltl.nl/leolani/n2mu")
class Friend(Person):
    pass


@emissor_dataclass
class LeolaniContext(ScenarioContext):
    speaker: Person
    persons: List[Person]
    objects: List[Object]