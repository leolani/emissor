import time

from emissor.annotation.constants import SPEAKER, DEFAULT_SIGNALS
from emissor.persistence import ScenarioStorage
from emissor.persistence.persistence import ScenarioController
from emissor.processing.api import ScenarioInitializer, ProcessorPlugin
from emissor.representation.scenario import Modality, Scenario, ScenarioContext

_DEFAULT_DURATION = 5 * 60


class AnnotationToolScenarioInitializer(ScenarioInitializer):
    def initialize_scenario(self, scenario_id: str, storage: ScenarioStorage):
        start = int(time.time())
        end = int(start + _DEFAULT_DURATION)

        scenario = Scenario.new_instance(scenario_id, start, end,
                                         ScenarioContext("robot_agent", SPEAKER, [], []),
                                         DEFAULT_SIGNALS)

        storage.save_scenario(scenario)

    def initialize_modality(self, scenario: ScenarioController, modality: Modality):
        pass


class AnnotationToolProcessorPlugin(ProcessorPlugin):
    def create_initializer(self) -> ScenarioInitializer:
        return AnnotationToolScenarioInitializer()

    @property
    def name(self) -> str:
        return "default"

    @property
    def priority(self) -> int:
        return 0
