from enum import Enum, auto
from typing import Iterable

import logging

from emissor.persistence import ScenarioStorage
from emissor.processing.api import DataPreprocessor, ScenarioInitializer, SignalProcessor
from emissor.representation.scenario import Modality

logger = logging.getLogger()


class Step(Enum):
    PREPROCESSING = auto()
    INIT = auto()
    PROCESS = auto()


class DataProcessing:
    def __init__(self, storage: ScenarioStorage, preprocessors: Iterable[DataPreprocessor],
                 scenario_initializer: ScenarioInitializer, signal_processors: Iterable[SignalProcessor]):
        self._storage = storage
        self._preprocessors = preprocessors
        self._scenario_initializer = scenario_initializer
        self._signal_processors = signal_processors

    def run_preprocessing(self):
        for preprocessor in self._preprocessors:
            with preprocessor:
                logger.info("Preprocessing dataset with %s to %s", preprocessor.__class__.__name__, self._storage.base_path)
                preprocessor.preprocess()
                logger.info("Finished preprocessing dataset with %s", preprocessor.__class__.__name__)

    def run_init(self):
        if not self._scenario_initializer:
            return

        logger.info("Initialize dataset %s", self._storage.base_path)
        with self._scenario_initializer:
            for scenario_id in self._storage.list_scenarios():
                try:
                    self._storage.load_scenario(scenario_id)
                    logger.debug("Scenario %s already initialized", scenario_id)
                    continue
                except ValueError:
                    pass

                self._scenario_initializer.initialize_scenario(scenario_id, self._storage)
                logger.info("Initialized scenario %s", scenario_id)

                for modality in Modality:
                    if self._storage.load_modality(scenario_id, modality):
                        logger.debug("Modality %s for scenario %s already initialized", modality, scenario_id)
                        continue

                    scenario = self._storage.load_scenario(scenario_id)
                    self._scenario_initializer.initialize_modality(modality, scenario, self._storage)
                    logger.info("Initialized modality %s for scenario %s", modality.name, scenario_id)

    def run_process(self):
        if not self._signal_processors:
            return

        logger.info("Processing scenarios with processors %s", [processor.name for processor in self._signal_processors])
        for processor in self._signal_processors:
            with processor:
                for scenario_id in self._storage.list_scenarios():
                    scenario = self._storage.load_scenario(scenario_id)
                    for modality in scenario.signals:
                        signals = self._storage.load_modality(scenario_id, Modality[modality.upper()])
                        processor.process(scenario, Modality[modality.upper()], signals, self._storage)

    def run(self):
        self.run_preprocessing()
        self.run_init()
        self.run_process()
