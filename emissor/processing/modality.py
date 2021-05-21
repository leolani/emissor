import argparse

import logging

import uuid
from pandas import Series
from typing import Iterable, Any

from emissor.annotation.persistence import ScenarioStorage
from emissor.representation.entity import Person, Gender
from emissor.representation.scenario import Scenario, ScenarioContext, Modality, ImageSignal, TextSignal, Signal


_SPEAKER = Person(str(uuid.uuid4()), "Speaker", 50, Gender.UNDEFINED)
_DEFAULT_SIGNALS = {
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
}


class ModalitySetup:
    def __init__(self, dataset: str, scenario_id: str, modality: Modality):
        self._storage = ScenarioStorage(dataset, mode="metadata")
        self._scenario_id = scenario_id
        self._modality = modality

    def run_setup(self):
        try:
            self.create_modality()
        except Exception:
            logging.exception("Modality %s could not be created for scenario %s", self._modality, self._scenario_id)

    def create_modality(self) -> Iterable[Signal[Any, Any]]:
        signals = self._storage.load_modality(self._scenario_id, self._modality)
        if signals is None:
            signals = self._create_modality_metadata()
            self._storage.save_signals(self._scenario_id, self._modality, signals)

        return signals

    def _create_modality_metadata(self) -> Iterable[Signal[Any, Any]]:
        scenario = self._storage.load_scenario(self._scenario_id)
        if self._modality == Modality.IMAGE:
            image_meta = self._storage.load_images(self._storage.load_scenario(self._scenario_id))
            return [self._create_image_signal(scenario, meta) for _, meta in image_meta.iterrows()]
        elif self._modality == Modality.TEXT:
            texts = self._storage.load_text(self._scenario_id)
            return [self._create_text_signal(scenario, utt) for utt in texts]
        else:
            raise ValueError("Unsupported modality " + self._modality.name)

    def _create_image_signal(self, scenario: Scenario, image_meta: Series) -> ImageSignal:
        bounds = image_meta['bounds']
        image_time = image_meta['time']
        file = image_meta['file']
        image_signal = ImageSignal.for_scenario(scenario.id, image_time, image_time, file, bounds)

        return image_signal

    def _create_text_signal(self, scenario: Scenario, utterance_data: dict):
        timestamp = utterance_data['time'] if 'time' in utterance_data else scenario.start
        utterance = utterance_data['utterance']
        signal = TextSignal.for_scenario(scenario.id, timestamp, timestamp, utterance_data['file'], utterance, [])

        return signal
