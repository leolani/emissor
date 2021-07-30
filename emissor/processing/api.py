from abc import ABC
from typing import Iterable, Any, Tuple, Mapping

from emissor.persistence import ScenarioStorage
from emissor.persistence.persistence import ScenarioController
from emissor.representation.scenario import Signal, Modality


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

    def initialize_modality(self, scenario: ScenarioController, modality: Modality):
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

    def scenario_key(self, storage: ScenarioStorage) -> Any:
        return None


class SignalProcessor(ABC):
    def process_signal(self, scenario: ScenarioController, signal: Signal):
        raise NotImplementedError("")

    def process_signals(self, scenario: ScenarioController, signals: Mapping[Modality, Iterable[Signal]]):
        for modality, signals in signals.items():
            for signal in signals:
                self.process_signal(scenario, signal)

    def process_scenario(self, scenario: ScenarioController):
        scenario.load_signals(self.modalities)
        self.process_signals(scenario, scenario.signals)

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def parallel(self) -> bool:
        return False

    @property
    def modalities(self) -> Tuple[Modality]:
        return ()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def scenario_key(self, storage: ScenarioStorage) -> Any:
        return None

    def signal_key(self, storage: ScenarioStorage) -> Any:
        return lambda signal: signal.time.start


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


