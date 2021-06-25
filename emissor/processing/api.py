from abc import ABC
from typing import Iterable

from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Scenario, Signal, Modality


class DataPreprocessor(ABC):
    def preprocess(self):
        raise NotImplementedError("")

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ScenarioInitializer(ABC):
    def initialize_scenario(self, scenario_id: str, storage: ScenarioStorage):
        raise NotImplementedError("")

    def initialize_modality(self, modality: Modality, scenario: Scenario, storage: ScenarioStorage):
        raise NotImplementedError("")

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def parallel(self) -> bool:
        return False

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class SignalProcessor(ABC):
    def process(self, scenario: Scenario, modality: Modality, signals: Iterable[Signal], storage: ScenarioStorage):
        raise NotImplementedError("")

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def parallel(self) -> bool:
        return False

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


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


