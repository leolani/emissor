# TODO This conflicts with marshmallow dataclass serialization
# Enable using the current class in type annotations
# from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass

from rdflib import URIRef, Namespace
from typing import Tuple, Any, Union, List

from emissor.representation.container import Sequence, AtomicContainer, AtomicRuler
from emissor.representation.ldschema import emissor_dataclass, LdId
from emissor.representation.util import Identifier

friends_namespace = Namespace("http://cltl.nl/leolani/friends/")
data_namespace = Namespace("http://cltl.nl/combot/signal/")
predicate_namespace = Namespace("http://cltl.nl/combot/predicate/")


class AnnotationType(enum.Enum):
    DISPLAY = 0
    PERSON = 1
    EMOTION = 2
    FRIEND = 2
    OBJECT = 3
    TOKEN = 4
    POS = 5
    NER = 6
    LINK = 7
    REPRESENTATION = 8


class ImageLabel(enum.Enum):
    FACE = 0


class EntityType(enum.Enum):
    PERSON = 0
    FRIEND = 1
    OBJECT = 2


@dataclass
class Entity:
    id: URIRef
    type: EntityType


@dataclass
class Token(AtomicContainer):
    @classmethod
    def for_string(cls, value: str):
        token_id = str(uuid.uuid4())
        return cls(token_id, AtomicRuler(token_id), value)


@dataclass
class NER(AtomicContainer):
    @classmethod
    def for_string(cls, value: str):
        entity_id = str(uuid.uuid4())
        return cls(entity_id, AtomicRuler(entity_id), value)


@dataclass
class Triple:
    subject: Entity
    predicate: URIRef
    object: Entity

    # TODO make this more generic, return Triple (see import of annotations)
    @classmethod
    def from_friends(cls, subject_id, predicate_id, object_id) -> Any:
        return cls(Entity(friends_namespace.term(subject_id), EntityType.FRIEND),
                   predicate_namespace.term(predicate_id),
                   Entity(friends_namespace.term(object_id), EntityType.FRIEND))


@dataclass
class Utterance(Sequence[str]):
    seq: List[str]
    chat_id: Identifier
    utterance: str
    tokens: Tuple[Token]


@dataclass
class Display:
    display: str


@dataclass
class EntityLink:
    annotates: Union[str, URIRef]

    @property
    def id(self):
        return self.annotates

    @property
    def value(self):
        return friends_namespace + str(self.annotates)
