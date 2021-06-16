from dataclasses import dataclass
from unittest import TestCase

import numpy as np
import rdflib
from numpy.testing import assert_array_equal
from typing import TypeVar

from emissor.representation.container import TemporalRuler, TemporalContainer, AtomicRuler, Index, \
    AtomicContainer, ArrayContainer, MultiIndex, Sequence
from emissor.representation.entity import Person, Gender
from emissor.representation.scenario import Scenario, ScenarioContext, TextSignal, Mention, Annotation, ImageSignal
from emissor.representation.util import marshal, unmarshal

T = TypeVar('T')

@dataclass
class TestData:
    x: str


class TestValue:
    def __init__(self, x: str):
        self.x = x

    def __eq__(self, other):
        return self.x == other.x


CONTAINER_INSTANCES = [
    TemporalRuler("container_id", 0, 1),
    TemporalContainer.from_range(0, 1),
    AtomicRuler("container_id"),
    AtomicContainer("id", AtomicRuler("id"), "1"),
    AtomicContainer("id", AtomicRuler("id"), 1),
    AtomicContainer("id", AtomicRuler("id"), TestData("1")),
    AtomicContainer("id", AtomicRuler("id"), TestValue("1")),
    Index.from_range("id", 0, 1),
    Sequence.from_seq(["1", "2", "3"]),
    Sequence.from_seq([1, 2, 3]),
    Sequence.from_seq([1.1, 2.2, 3.3]),
    Sequence.from_seq([TestData("1"), TestData("2"), TestData("3")]),
    MultiIndex("id", (1, 2, 3, 4))
]


SCENARIO_INSTANCES = [
    Annotation("1", "2", "3", 4),
    Mention("id", [Index.from_range("id", 0, 1)],
            [Annotation("type", "val", "source", 0)]),
    TextSignal.for_scenario("id", 0, 1, "file.txt", "text", []),
    TextSignal.for_scenario("id", 0, 1, "file.txt", "text",
                            [Mention("id", [Index.from_range("id", 0, 1)],
                                     [Annotation("type", "val", "source", 0)])]),
    ImageSignal.for_scenario("id", 0, 1, "file.txt", (1, 2, 3, 4), []),
    ImageSignal.for_scenario("id", 0, 1, "file.txt", (1, 2, 3, 4),
                             [Mention("id", [MultiIndex("id", (0, 0, 1, 1))],
                                      [Annotation("type", "val", "source", 0)])]),
    ScenarioContext("agent", Person("id", "name", 18, Gender.MALE), [], []),
    Scenario.new_instance("scenario1", 0, 10, ScenarioContext("agent", Person("id", "name", 18, Gender.MALE), [], []),
                          {})
]


class TestMarshallingDomain(TestCase):
    def test_marshalling_containers(self):
        for instance in CONTAINER_INSTANCES:
            with self.subTest(str(instance.__class__.__name__)):
                serialized = marshal(instance, cls=instance.__class__)
                clone = unmarshal(serialized, cls=instance.__class__)
                self.assertEqual(instance, clone)

    def test_marshalling_array_container(self):
        array_container = ArrayContainer.from_array(np.array([[1.1, 2.2], [3.3, 4.4]]))

        clone = unmarshal(marshal(array_container, cls=ArrayContainer), cls=ArrayContainer)

        assert_array_equal(array_container.array, clone.array)

    def test_marshalling_scenario(self):
        instances = SCENARIO_INSTANCES

        for instance in instances:
            with self.subTest(str(instance.__class__.__name__)):
                serialized = marshal(instance, cls=instance.__class__)
                clone = unmarshal(serialized, cls=instance.__class__)
                self.assertEqual(instance, clone)

    def test_json_ld(self):
        for instance in CONTAINER_INSTANCES + SCENARIO_INSTANCES:
            with self.subTest(str(instance.__class__.__name__)):
                serialized = marshal(instance, cls=instance.__class__)
                graph = rdflib.Graph()
                graph.parse(data=serialized, format="json-ld")

                self.assertGreater(len(graph), 0)