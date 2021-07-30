import logging
from joblib import Parallel, delayed
from typing import Iterable

from emissor.persistence import ScenarioStorage
from emissor.processing.api import DataPreprocessor, ScenarioInitializer, SignalProcessor
from emissor.representation.scenario import Modality

logger = logging.getLogger(__name__)


class DataProcessing:
    def __init__(self, storage: ScenarioStorage, preprocessors: Iterable[DataPreprocessor],
                 scenario_initializer: ScenarioInitializer, signal_processors: Iterable[SignalProcessor],
                 num_jobs: int = 1):
        self._storage = storage
        self._preprocessors = preprocessors
        self._scenario_initializer = scenario_initializer
        self._signal_processors = signal_processors
        self._num_jobs = num_jobs

    def run(self):
        self.run_preprocessing()
        self.run_init()
        self.run_process()

    def run_preprocessing(self):
        for preprocessor in self._preprocessors:
            with preprocessor:
                logger.info("Preprocessing dataset with %s to %s", preprocessor.name, self._storage.base_path)
                preprocessor.preprocess()
                logger.info("Finished preprocessing dataset with %s", preprocessor.name)

    def run_init(self):
        if not self._scenario_initializer:
            return

        logger.info("Initialize scenarios %s with %s", self._storage.base_path, self._scenario_initializer.name)
        with self._scenario_initializer:
            self.execute_for_scenarios(_initialize, self._scenario_initializer)

    def run_process(self):
        if not self._signal_processors:
            return

        logger.info("Processing scenarios with processors %s", [processor.name for processor in self._signal_processors])
        for processor in self._signal_processors:
            with processor:
                self.execute_for_scenarios(_process, processor)

    def execute_for_scenarios(self, function, task):
        scenario_ids = tuple(sorted(self._storage.list_scenarios(), key=task.scenario_key(self._storage)))
        if not task.parallel:
            for scenario_id in scenario_ids:
                function(self._storage.base_path, task, scenario_id)
        else:
            scenario_ids = tuple(scenario_ids)
            num_jobs = min(self._num_jobs, len(scenario_ids))
            Parallel(n_jobs=num_jobs)(
                delayed(function)(self._storage.base_path, task, scenario_id)
                for scenario_id in scenario_ids)


def _initialize(base_path, scenario_initializer, scenario_id):
    storage = ScenarioStorage(base_path)
    try:
        storage.load_scenario(scenario_id)
        logger.debug("Scenario %s already initialized", scenario_id)
        return
    except ValueError:
        pass

    scenario_initializer.initialize_scenario(scenario_id, storage)
    logger.info("Initialized scenario %s", scenario_id)

    scenario = storage.load_scenario(scenario_id)
    for modality in Modality:
        if modality in scenario.signals:
            logger.debug("Modality %s for scenario %s already initialized", modality, scenario_id)
            continue

        scenario_initializer.initialize_modality(scenario, modality)
        logger.info("Initialized modality %s for scenario %s", modality.name, scenario_id)

    storage.save_scenario(scenario)


def _process(base_path, processor, scenario_id):
    storage = ScenarioStorage(base_path)

    logger.info("Processing scenario %s with processor %s", scenario_id, processor.name)

    scenario = storage.load_scenario(scenario_id)
    processor.process_scenario(scenario)
    storage.save_scenario(scenario)

# TODO
def _signal_generator(scenario_id, modality, processor, storage):
    signals = storage.load_modality(scenario_id, Modality[modality.upper()])

    for signal in sorted(signals, key=processor.signal_key(storage)):
        yield signal