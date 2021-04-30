# Define Annotation Class
from __future__ import annotations

import dataclasses
from abc import ABC
from dataclasses import dataclass

import numpy as np
import uuid
from typing import Union, TypeVar, Generic, Iterable, Tuple, Type, Any

from emissor.representation.util import Identifier, Typed, marshal


@dataclass
class Ruler(Typed, ABC):
    """Base type of Rulers that allow to identify a segment relative to a ruler in a signal"""
    container_id: Identifier


R = TypeVar('R', bound=Ruler)
T = TypeVar('T')


class Container(Generic[R, T], ABC):
    def __getitem__(self, segment: R) -> T:
        raise NotImplementedError()


@dataclass
class BaseContainer(Container[R, T], Typed, ABC):
    id: Identifier
    ruler: R


@dataclass
class Index(Ruler):
    start: int
    stop: int

    @classmethod
    def from_range(cls: Type[T], start: int, stop: int) -> T:
        return cls(None, start, stop)

    def get_offset(self, start: int, end: int) -> Index:
        if start < self.start or end > self.stop:
            raise ValueError(f"start and end must be within [{self.start}, {self.stop}), was [{start}, {end})")

        return Index(self.container_id, start, end)


@dataclass
class Sequence(BaseContainer[Index, T]):
    start: int
    stop: int
    seq: Tuple[T, ...]

    @classmethod
    def from_seq(cls: Type[T], seq: Iterable[Any]) -> T:
        seq_tuple = tuple(seq)
        ruler = Index.from_range(0, len(seq_tuple))
        return cls(str(uuid.uuid4()), ruler, ruler.start, ruler.stop, seq_tuple)

    def __getitem__(self, offset: Index) -> T:
        return self.seq[offset.start:offset.stop]


@dataclass
class MultiIndex(Ruler):
    bounds: Tuple[int, int, int, int]

    def get_area_bounding_box(self, x_min: int, y_min: int, x_max: int, y_max: int) -> MultiIndex:
        if x_min < self.bounds[0] or x_max > self.bounds[2] \
                or y_min < self.bounds[1] or y_max > self.bounds[3]:
            raise ValueError(f"bounds must be within {self.bounds}, was {x_min}, {y_min}, {x_max}, {y_max}")

        return MultiIndex(self.container_id, (x_min, y_min, x_max, y_max))


@dataclass
class ArrayContainer(BaseContainer[MultiIndex, np.array]):
    array: np.ndarray

    @classmethod
    def from_array(cls: Type[T], array_: Union[tuple, list, np.ndarray]) -> T:
        value = np.array(array_)
        ruler = MultiIndex(None, (0, 0, value.shape[0], value.shape[1]))
        return cls(str(uuid.uuid4()), ruler, value)

    @property
    def bounds(self):
        return self.ruler.bounds

    def __getitem__(self, bounding_box: MultiIndex) -> np.array:
        b = bounding_box.bounds
        return self.array[b[0]:b[1], b[1]:b[3]]


@dataclass
class TemporalRuler(Ruler):
    start: int
    end: int

    def get_time_segment(self, start: int, end: int) -> TemporalRuler:
        if start < self.start or end >= self.end:
            raise ValueError(f"start and end must be within [{self.start}, {self.end}), was [{start}, {end})")

        return TemporalRuler(self.container_id, start, end)


@dataclass
class TemporalContainer(BaseContainer[TemporalRuler, TemporalRuler]):
    @classmethod
    def from_range(cls: Type[T], start: int, end: int) -> T:
        return cls(str(uuid.uuid4()), TemporalRuler(None, start, end))

    @property
    def start(self):
        return self.ruler.start

    @property
    def end(self):
        return self.ruler.end

    def __getitem__(self, segment: TemporalRuler) -> TemporalRuler:
        return segment


@dataclass
class AtomicRuler(Ruler):
    pass


@dataclass
class AtomicContainer(BaseContainer[AtomicRuler, T]):
    value: T

    def __getitem__(self, segment: AtomicRuler) -> T:
        if not segment.container_id == self.id:
            raise ValueError("Invalid segment")

        return self.value


if __name__ == "__main__":
    from pprint import pprint

    tokens = Sequence.from_seq(["I", "am", "in", "Amsterdam"])
    token_offset = tokens.ruler.get_offset(0, 1)
    token_segment = tokens[token_offset]
    pprint(token_segment)
    print(marshal(tokens))

    array = ArrayContainer.from_array(np.zeros((5, 5, 3), dtype=int))
    bbox = array.ruler.get_area_bounding_box(0, 0, 2, 2)
    area = array[bbox]
    pprint(area)
    print(marshal(array))

    period = TemporalContainer.from_range(0, 1000)
    time_segment = period.ruler.get_time_segment(10, 100)
    sub_period = period[time_segment]
    print(sub_period)
    print(marshal(period))