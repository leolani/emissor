# TODO This conflicts with marshmallow dataclass serialization
# Enable using the current class in type annotations
# from __future__ import annotations

import numpy as np
import uuid
from abc import ABC
from numpy.typing import ArrayLike
from typing import TypeVar, Generic, Iterable, Tuple, Type, Any, List

from emissor.representation.ldschema import emissor_dataclass, LdId
from emissor.representation.util import Identifier, get_serializable_type_var


@emissor_dataclass
class Ruler(ABC):
    """Base type of Rulers that allow to identify a segment relative to a ruler in a signal"""
    container_id: Identifier = LdId()


C = TypeVar('C')
R = get_serializable_type_var('R', bound=Ruler)
T = get_serializable_type_var('T')


@emissor_dataclass
class Container(Generic[R, T], ABC):
    def get_segment(self, segment: R) -> T:
        raise NotImplementedError()


@emissor_dataclass
class BaseContainer(Generic[R, T], Container[R, T]):
    id: Identifier
    ruler: R


@emissor_dataclass
class Index(Ruler):
    start: int
    stop: int

    @classmethod
    def from_range(cls: Type[C], container_id: Identifier, start: int, stop: int) -> C:
        return cls(container_id, start, stop)

    # TODO return Index (see import of annotations)
    def get_offset(self, start: int, end: int) -> Any:
        if start < self.start or end > self.stop:
            raise ValueError(f"start and end must be within [{self.start}, {self.stop}), was [{start}, {end})")

        return Index(self.container_id, start, end)


@emissor_dataclass
class Sequence(Generic[T], BaseContainer[Index, T]):
    seq: List[T]

    @classmethod
    def from_seq(cls: Type[C], seq: Iterable[Any]) -> C:
        seq_tuple = list(seq)
        sequence_id = str(uuid.uuid4())
        ruler = Index.from_range(sequence_id, 0, len(seq_tuple))

        return cls(sequence_id, ruler, seq_tuple)

    def get_segment(self, offset: Index) -> T:
        return self.seq[offset.start:offset.stop]


@emissor_dataclass
class MultiIndex(Ruler):
    bounds: Tuple[int, int, int, int]

    # TODO return MultiIndex (see import of annotations)
    def get_area_bounding_box(self, x_min: int, y_min: int, x_max: int, y_max: int) -> Any:
        if x_min < self.bounds[0] or x_max > self.bounds[2] \
                or y_min < self.bounds[1] or y_max > self.bounds[3]:
            raise ValueError(f"bounds must be within {self.bounds}, was {x_min}, {y_min}, {x_max}, {y_max}")

        return MultiIndex(self.container_id, (x_min, y_min, x_max, y_max))


@emissor_dataclass
class ArrayContainer(BaseContainer[MultiIndex, ArrayLike]):
    array: ArrayLike

    @classmethod
    def from_array(cls: Type[C], array_: ArrayLike) -> C:
        value = np.array(array_)
        container_id = str(uuid.uuid4())
        ruler = MultiIndex(container_id, (0, 0, value.shape[0], value.shape[1]))

        return cls(container_id, ruler, value)

    @property
    def bounds(self):
        return self.ruler.bounds

    def get_segment(self, bounding_box: MultiIndex) -> np.array:
        b = bounding_box.bounds

        return self.array[b[0]:b[1], b[1]:b[3]]


@emissor_dataclass
class TemporalRuler(Ruler):
    start: int
    end: int

    # TODO return TemporalRuler (see import of annotations)
    def get_time_segment(self, start: int, end: int) -> Any:
        if start < self.start or end >= self.end:
            raise ValueError(f"start and end must be within [{self.start}, {self.end}), was [{start}, {end})")

        return TemporalRuler(self.container_id, start, end)


@emissor_dataclass
class TemporalContainer(BaseContainer[TemporalRuler, TemporalRuler]):
    @classmethod
    def from_range(cls: Type[C], start: int, end: int) -> C:
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
class AtomicContainer(Generic[T], BaseContainer[AtomicRuler, T]):
    value: T

    def get_segment(self, segment: AtomicRuler) -> T:
        if not segment.container_id == self.id:
            raise ValueError("Invalid segment")

        return self.value
