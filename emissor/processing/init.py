import argparse
import logging
import uuid

from emissor.annotation.persistence import ScenarioStorage
from emissor.processing.modality import ModalitySetup
from emissor.representation.entity import Person, Gender
from emissor.representation.scenario import Scenario, ScenarioContext, Modality

_AGENT = "robot_agent"
_SPEAKER = Person(str(uuid.uuid4()), "Speaker", 50, Gender.UNDEFINED)
_DEFAULT_SIGNALS = {
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
}

_DEFAULT_MODALITIES = (Modality.TEXT, Modality.IMAGE)


logger = logging.getLogger(__name__)


def run_init(dataset):
    storage = ScenarioStorage(dataset, mode="metadata")
    for scenario_id in storage.list_scenarios():
        create_scenario(scenario_id, storage)
        logger.info("Initialized scenario %s", scenario_id)

        for modality in _DEFAULT_MODALITIES:
            ModalitySetup(dataset, scenario_id, modality).run_setup()
            logger.info("Initialized modality %s for scenario %s", modality.name, scenario_id)


def create_scenario(scenario_id: str, storage: ScenarioStorage) -> Scenario:
    scenario = storage.load_scenario(scenario_id)
    if not scenario:
        scenario = _create_scenario_metadata(scenario_id, storage)
        storage.save_scenario(scenario)

    return scenario


def _create_scenario_metadata(scenario_id: str, storage: ScenarioStorage) -> Scenario:
    # TODO plugin for scenario details
    start, end = storage.guess_scenario_range(scenario_id, _DEFAULT_SIGNALS.keys())

    return Scenario.new_instance(scenario_id, start, end,
                                 ScenarioContext(_AGENT, _SPEAKER, [], []),
                                 _DEFAULT_SIGNALS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup EMISSOR metadata for a dataset.')
    parser.add_argument('--dataset', type=str,
                        help="Base directory that contains the scenarios of the dataset.")

    args = parser.parse_args()
    logging.info("Setting up EMISSOR for dataset %s", args.dataset)

    run_init(args.dataset)