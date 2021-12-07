# TODO This conflicts with marshmallow dataclass serialization
# Enable using the current class in type annotations
# from __future__ import annotations

"""
Basic classes for values used in :class:`emissor.representation.Annotation`.
"""
from dataclasses import dataclass
from enum import Enum, auto

import uuid
from rdflib import URIRef, Namespace
from typing import Any, List

from emissor.representation.container import Sequence, AtomicContainer, AtomicRuler
from emissor.representation.ldschema import LdId, emissor_dataclass
from emissor.representation.util import Identifier

friends_namespace = Namespace("http://cltl.nl/leolani/friends/")
data_namespace = Namespace("http://cltl.nl/combot/signal/")
predicate_namespace = Namespace("http://cltl.nl/combot/predicate/")


class AnnotationType(Enum):
    DISPLAY = auto()
    PERSON = auto()
    EMOTION = auto()
    FRIEND = auto()
    OBJECT = auto()
    TOKEN = auto()
    POS = auto()
    NER = auto()
    LINK = auto()
    REPRESENTATION = auto()
    UTTERANCE = auto()


class ImageLabel(Enum):
    FACE = auto()


class EntityType(Enum):
    PERSON = auto()
    FRIEND = auto()
    OBJECT = auto()


@emissor_dataclass
class Entity:
    id: URIRef = LdId()


@dataclass
class Token(AtomicContainer[str]):
    @classmethod
    def for_string(cls, value: str):
        token_id = str(uuid.uuid4())
        return cls(token_id, AtomicRuler(token_id), value)


@dataclass
class NER(AtomicContainer[str]):
    @classmethod
    def for_string(cls, value: str):
        token_id = str(uuid.uuid4())
        return cls(token_id, AtomicRuler(token_id), value)


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
class Utterance(Sequence):
    chat_id: Identifier
    utterance: str
    tokens: List[Token]


@dataclass
class Display:
    display: str
