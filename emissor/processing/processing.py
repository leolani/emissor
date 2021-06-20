from enum import Enum, auto

import logging

from emissor.representation.scenario import Modality

logger = logging.getLogger()


class Step(Enum):
    PREPROCESSING = auto()
    INIT = auto()
    PROCESS = auto()


class DataProcessing:
    def __init__(self, storage, preprocessors, scenario_initializer, signal_processors):
        self._storage = storage
        self._preprocessors = preprocessors
        self._scenario_initializer = scenario_initializer
        self._signal_processors = signal_processors

    def run_preprocessing(self):
        for preprocessor in self._preprocessors:
            logger.info("Preprocessing dataset with %s to %s", preprocessor.__class__.__name__, self._storage.base_path)
            preprocessor.preprocess(self._storage.base_path)
            logger.info("Finished preprocessing dataset with %s", preprocessor.__class__.__name__)

    def run_init(self):
        if not self._scenario_initializer:
            return

        logger.info("Initialize dataset %s", self._storage.base_path)
        for scenario_id in self._storage.list_scenarios():
            self._scenario_initializer.initialize_scenario(scenario_id, self._storage)
            logger.info("Initialized scenario %s", scenario_id)

            for modality in Modality:
                self._scenario_initializer.initialize_modality(modality, self._storage.load_scenario(scenario_id),
                                                               self._storage)
                logger.info("Initialized modality %s for scenario %s", modality.name, scenario_id)

    def run_process(self):
        if not self._signal_processors:
            return

        logger.info("Processing scenarios with processors {}", [processor.name for processor in self._signal_processors])
        for scenario_id in self._storage.list_scenarios():
            scenario = self._storage.load_scenario(scenario_id)

            [processor.process(scenario, modality, self._storage)
             for processor in self._signal_processors
             for modality in scenario.signals]

    def run(self):
        self.run_init()
        self.run_preprocessing()
        self.run_process()
