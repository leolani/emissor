import os
import uuid
from glob import glob

import json
import sys

from grmc.representation.entity import Person, Gender
from grmc.representation.scenario import Scenario, ScenarioContext, Modality
from grmc.representation.util import serializer

base_path = sys.argv[0]

_SPEAKER = Person(uuid.uuid4(), "Speaker", 50, Gender.UNDEFINED)
_DEFAULT_SIGNAL_METADATA = {
        Modality.IMAGE: "./image.json",
        Modality.TEXT: "./text.json"
    }


def get_base():
    return "webapp/src/assets"


def get_path(scenario_name, modality=None):
    path = os.path.join(get_base(), scenario_name)
    if modality:
        path = os.path.join(path, modality + ".json")
    else:
        path = os.path.join(path, scenario_name + ".json")

    return path


def list_scenarios():
    return tuple(os.path.basename(path[:-1]) for path in glob(os.path.join(get_base(),"*", "")))


def load_scenario(scenario):
    scenario_metadata = get_path(scenario)
    _ensure_scenario_metadata(scenario_metadata)
    with open(scenario_metadata) as json_file:
        return json.load(json_file)


def _ensure_scenario_metadata(scenario_metadata):
    if not os.path.isfile(scenario_metadata):
        scenario = Scenario(uuid.uuid4(), 0, 1,
                            ScenarioContext("robot_agent", _SPEAKER, [], []),
                            _DEFAULT_SIGNAL_METADATA)
        with open(scenario_metadata, 'w') as json_file:
            json.dump(scenario, json_file, default=serializer, indent=2)


def load_modality(scenario, modality):
    modality_metadata = get_path(scenario, modality)
    _ensure_modality_metadata(modality_metadata)
    with open(modality_metadata) as json_file:
        return json.load(json_file)


def _ensure_modality_metadata(modality_metadata):
    if not os.path.isfile(modality_metadata):
        with open(modality_metadata, 'w') as json_file:
            json.dump([], json_file, default=serializer, indent=2)


def add_annotation(scenario, modality):
    signals = {sig.id: sig for sig in load_modality(scenario, modality)}
    print(json.dumps(signals, default=serializer))
