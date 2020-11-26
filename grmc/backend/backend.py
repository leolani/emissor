import os
from glob import glob

import pandas as pd
import sys
import time
import uuid
from PIL import Image
from pandas import Series
from typing import Iterable, Any

from grmc.backend.persistence import ScenarioStorage, guess_scenario_range, load_images, ANNOTATION_TOOL_ID, file_name, \
    load_text
from grmc.representation.annotation import AnnotationType
from grmc.representation.container import TemporalRuler
from grmc.representation.entity import Person, Gender
from grmc.representation.scenario import Scenario, ScenarioContext, Modality, ImageSignal, TextSignal, Mention, \
    Annotation, Signal

base_path = sys.argv[0]

_SPEAKER = Person(str(uuid.uuid4()), "Speaker", 50, Gender.UNDEFINED)
_DEFAULT_SIGNALS = {
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
}


def _get_start_ruler(scenario_meta):
    return TemporalRuler(scenario_meta.id, scenario_meta.start, scenario_meta.start)


def create_image_signal(scenario: Scenario, image_meta: Series) -> ImageSignal:
    bounds = image_meta['bounds']
    image_time = image_meta['time']
    file = image_meta['file']
    image_signal = ImageSignal.for_scenario(scenario.id, image_time, image_time, file, bounds)

    display_annotation = Annotation(AnnotationType.DISPLAY.name.lower(), file_name(file), ANNOTATION_TOOL_ID,
                                    int(time.time()))
    display = Mention([image_signal.ruler.get_area_bounding_box(*bounds)], [display_annotation])
    image_signal.mentions.append(display)

    return image_signal


def _create_text_signal(scenario: Scenario, utt: Series):
    timestamp = utt['time'] if 'time' in utt else scenario.start

    mentions = []

    return TextSignal.for_scenario(scenario.id, timestamp, timestamp, utt['file'], utt['utterance'], mentions)


class Backend:
    def __init__(self):
        self._storage = ScenarioStorage()

    def list_scenarios(self) -> Iterable[str]:
        return self._storage.list_scenarios()

    def load_scenario(self, scenario_id: str) -> Scenario:
        scenario = self._storage.load_scenario(scenario_id)
        if not scenario:
            scenario = self._create_scenario(scenario_id)
            self._storage.save_scenario(scenario)

        return scenario

    def _create_scenario(self, scenario_id: str) -> Scenario:
        start, end = guess_scenario_range(scenario_id, _DEFAULT_SIGNALS.keys())

        return Scenario.new_instance(scenario_id, start, end,
                                     ScenarioContext("robot_agent", _SPEAKER, [], []),
                                     _DEFAULT_SIGNALS)

    def load_modality(self, scenario_id: str, modality) -> Iterable[Signal[Any, Any]]:
        signals = self._storage.load_modality(scenario_id, modality)
        if signals is None:
            signals = self._create_modality_metadata(scenario_id, modality)
            self._storage.save_signals(scenario_id, modality, signals)

        return signals

    def _create_modality_metadata(self, scenario_id, modality) -> Iterable[Signal[Any, Any]]:
        scenario = self.load_scenario(scenario_id)
        if modality.lower() == "image":
            image_meta = load_images(self._storage.load_scenario(scenario_id))
            return [create_image_signal(scenario, meta) for _, meta in image_meta.iterrows()]
        elif modality.lower() == "text":
            texts = load_text(scenario_id)
            return [_create_text_signal(scenario, utt) for _, utt in texts.iterrows()]
        else:
            raise ValueError("Unsupported modality " + modality)


    def save_signal(self, scenario_id, signal):
        self._storage.save_signal(scenario_id, signal)
