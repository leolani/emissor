# Define Annotation Class
from __future__ import annotations

import enum
from dataclasses import dataclass

from rdflib import URIRef, Namespace
from typing import Tuple

from grmc.representation.container import Sequence, AtomicContainer
from grmc.representation.util import Identifier

friends_namespace = Namespace("http://cltl.nl/leolani/friends/")
data_namespace = Namespace("http://cltl.nl/combot/signal/")
predicate_namespace = Namespace("http://cltl.nl/combot/predicate/")


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
class Triple:
    subject: Entity
    predicate: URIRef
    object: Entity

    # TODO make this more generic
    @classmethod
    def from_friends(cls, subject_id, predicate_id, object_id) -> Triple:
        return cls(Entity(friends_namespace.term(subject_id), EntityType.FRIEND),
                   predicate_namespace.term(predicate_id),
                   Entity(friends_namespace.term(object_id), EntityType.FRIEND))


@dataclass
class Token(AtomicContainer):
    pass


@dataclass
class Utterance(Sequence):
    chat_id: Identifier
    utterance: str
    tokens: Tuple[Token]


@dataclass
class Display:
    display: str
