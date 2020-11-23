import os
from glob import glob
import pandas as pd

import json
import sys
import uuid
import jsonpickle

from grmc.representation.container import TemporalRuler
from grmc.representation.entity import Person, Gender
from grmc.representation.scenario import Scenario, ScenarioContext, Modality, Signal, ImageSignal, TextSignal
from grmc.representation.util import serializer

jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
jsonpickle.set_preferred_backend('simplejson')

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
    _ensure_scenario_metadata(scenario, scenario_metadata)
    with open(scenario_metadata) as json_file:
        json_string = json_file.read()
        return jsonpickle.decode(json_string)


def _ensure_scenario_metadata(scenario, scenario_metadata):
    if not os.path.isfile(scenario_metadata):
        scenario = Scenario(scenario, 0, 1,
                            ScenarioContext("robot_agent", _SPEAKER, [], []),
                            _DEFAULT_SIGNAL_METADATA)
        with open(scenario_metadata, 'w') as json_file:
            json_string = jsonpickle.encode(scenario, make_refs=False)
            json_file.write(json_string)


def load_modality(scenario, modality):
    modality_metadata = get_path(scenario, modality)
    _ensure_modality_metadata(modality_metadata, scenario, modality)
    with open(modality_metadata) as json_file:
        return jsonpickle.decode(json_file.read())


def _ensure_modality_metadata(modality_metadata, scenario, modality):
    scenarioMeta = load_scenario(scenario)
    if modality.lower() == "image":
        image_path = get_path(scenario, modality)[:-5]
        images = glob(os.path.join(image_path, "*"))
        signals = [ImageSignal(uuid.uuid4(), get_start_ruler(scenarioMeta), ["image/" + os.path.basename(image)], ((0, 0, 0, 0)))
                   for image in images]
    if modality.lower() == "text":
        text_path = get_path(scenario, modality)[:-5]
        csv_files = glob(os.path.join(text_path, "*.csv"))
        if len(csv_files):
            utterances = pd.concat([pd.read_csv(f, quotechar='"', sep=',',skipinitialspace=True) for f in csv_files])
            signals = [TextSignal(uuid.uuid4(), get_start_ruler(scenarioMeta), [], len(utt), [], seq=utt)
                       for utt in utterances["utterance"]]
        else:
            signals = []

    if not os.path.isfile(modality_metadata):
        with open(modality_metadata, 'w') as json_file:
            json_file.write(jsonpickle.encode(signals, make_refs=False))


def get_start_ruler(scenarioMeta):
    return TemporalRuler(scenarioMeta.id, scenarioMeta.start, scenarioMeta.start)


def add_annotation(scenario, modality):
    signals = {sig.id: sig for sig in load_modality(scenario, modality)}
    print(json.dumps(signals, default=serializer))
