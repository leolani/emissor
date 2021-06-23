from os import PathLike

from abc import ABC
from argparse import Namespace, ArgumentParser
from typing import Iterable, Collection

from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Scenario, Signal, Modality


class DataPreprocessor(ABC):
    def preprocess(self):
        raise NotImplementedError("")

    @property
    def name(self) -> str:
        return self.__class__.__name__


class ScenarioInitializer(ABC):
    def initialize_scenario(self, scenario_id: str, storage: ScenarioStorage):
        raise NotImplementedError("")

    def initialize_modality(self, modality: Modality, scenario: Scenario, storage: ScenarioStorage):
        raise NotImplementedError("")

    @property
    def name(self) -> str:
        return self.__class__.__name__


class SignalProcessor(ABC):
    def process(self, scenario: Scenario, modality: Modality, signals: Iterable[Signal], storage: ScenarioStorage):
        raise NotImplementedError("")

    @property
    def name(self) -> str:
        return self.__class__.__name__


class ProcessorPlugin:
    def create_preprocessor(self) -> DataPreprocessor:
        return None

    def create_initializer(self) -> ScenarioInitializer:
        return None

    def create_processors(self) -> Iterable[SignalProcessor]:
        return []

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def priority(self) -> int:
        return 0


