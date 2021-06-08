# TODO This conflicts with marshmallow dataclass serialization
# Enable using the current class in type annotations
# from __future__ import annotations
import marshmallow
import uuid
from abc import ABC
from dataclasses import dataclass, field

from numpy.typing import ArrayLike
from typing import Union, TypeVar, Generic, Iterable, Tuple, Type, Any, List

import numpy as np

from emissor.representation.ldschema import emissor_dataclass
from emissor.representation.util import Identifier, marshal, ArrayLikeField


@dataclass
class Ruler(ABC):
    """Base type of Rulers that allow to identify a segment relative to a ruler in a signal"""
    container_id: Identifier


C_Ruler = TypeVar('C_Ruler', bound=Ruler)
C_Element = TypeVar('C_Element')
@dataclass
class Container(Generic[C_Ruler, C_Element], ABC):
    def get_segment(self, segment: C_Ruler) -> C_Element:
        raise NotImplementedError()


BC_Ruler = TypeVar('BC_Ruler', bound=Ruler)
BC_Element = TypeVar('BC_Element')
@dataclass
class BaseContainer(Container[BC_Ruler, BC_Element], ABC):
    id: Identifier
    ruler: BC_Ruler


I = TypeVar('I')
@emissor_dataclass
class Index(Ruler):
    start: int
    stop: int

    @classmethod
    def from_range(cls: Type[I], container_id: Identifier, start: int, stop: int) -> I:
        return cls(container_id, start, stop)

    # TODO return Index (see import of annotations)
    def get_offset(self, start: int, end: int) -> Any:
        if start < self.start or end > self.stop:
            raise ValueError(f"start and end must be within [{self.start}, {self.stop}), was [{start}, {end})")

        return Index(self.container_id, start, end)


S = TypeVar('S')
S_Element = TypeVar('S_Element')
@emissor_dataclass
class Sequence(BaseContainer[Index, S_Element]):
    ruler: Index
    start: int
    stop: int
    seq: List[S_Element]

    @classmethod
    def from_seq(cls: Type[S], seq: Iterable[Any]) -> S:
        seq_tuple = tuple(seq)
        sequence_id = str(uuid.uuid4())
        ruler = Index.from_range(sequence_id, 0, len(seq_tuple))
        return cls(sequence_id, ruler, ruler.start, ruler.stop, seq_tuple)

    def get_segment(self, offset: Index) -> S:
        return self.seq[offset.start:offset.stop]


MI = TypeVar('MI')
@emissor_dataclass
class MultiIndex(Ruler):
    bounds: Tuple[int, int, int, int]

    # TODO return MultiIndex (see import of annotations)
    def get_area_bounding_box(self, x_min: int, y_min: int, x_max: int, y_max: int) -> MI:
        if x_min < self.bounds[0] or x_max > self.bounds[2] \
                or y_min < self.bounds[1] or y_max > self.bounds[3]:
            raise ValueError(f"bounds must be within {self.bounds}, was {x_min}, {y_min}, {x_max}, {y_max}")

        return MultiIndex(self.container_id, (x_min, y_min, x_max, y_max))


AC = TypeVar('AC')
@emissor_dataclass
class ArrayContainer(BaseContainer[MultiIndex, ArrayLike]):
    ruler: MultiIndex
    array: ArrayLike

    @classmethod
    def from_array(cls: Type[AC], array_: Union[tuple, list, np.ndarray]) -> AC:
        value = np.array(array_)
        container_id = str(uuid.uuid4())
        ruler = MultiIndex(container_id, (0, 0, value.shape[0], value.shape[1]))
        return cls(container_id, ruler, value)

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return self.ruler.bounds

    def get_segment(self, bounding_box: MultiIndex) -> np.array:
        b = bounding_box.bounds
        return self.array[b[0]:b[1], b[1]:b[3]]


TR = TypeVar('TR')
@emissor_dataclass
class TemporalRuler(Ruler):
    start: int
    end: int

    # TODO return TemporalRuler (see import of annotations)
    def get_time_segment(self, start: int, end: int) -> TR:
        if start < self.start or end >= self.end:
            raise ValueError(f"start and end must be within [{self.start}, {self.end}), was [{start}, {end})")

        return TemporalRuler(self.container_id, start, end)


TC = TypeVar('TC')
@emissor_dataclass
class TemporalContainer(BaseContainer[TemporalRuler, TemporalRuler]):
    ruler: TemporalRuler

    @classmethod
    def from_range(cls: Type[TC], start: int, end: int) -> TC:
        id = str(uuid.uuid4())
        return cls(id, TemporalRuler(id, start, end))

    @property
    def start(self):
        return self.ruler.start

    @property
    def end(self):
        return self.ruler.end

    def get_segment(self, segment: TemporalRuler) -> TemporalRuler:
        return segment


@emissor_dataclass
class AtomicRuler(Ruler):
    pass


@emissor_dataclass
class AtomicContainer(BaseContainer[AtomicRuler, Any]):
    ruler: AtomicRuler
    value: Any

    def get_segment(self, segment: AtomicRuler) -> Any:
        if not segment.container_id == self.id:
            raise ValueError("Invalid segment")

        return self.value


if __name__ == "__main__":
    from pprint import pprint

    tokens = Sequence.from_seq(["I", "am", "in", "Amsterdam"])
    token_offset = tokens.ruler.get_offset(0, 1)
    token_segment = tokens.get_segment(token_offset)
    pprint(token_segment)
    print(marshal(tokens))

    array = ArrayContainer.from_array(np.zeros((5, 5, 3), dtype=int))
    bbox = array.ruler.get_area_bounding_box(0, 0, 2, 2)
    area = array.get_segment(bbox)
    pprint(area)
    print(marshal(array))

    period = TemporalContainer.from_range(0, 1000)
    time_segment = period.ruler.get_time_segment(10, 100)
    sub_period = period.get_segment(time_segment)
    print(period)
    print(marshal(period, cls=TemporalContainer))