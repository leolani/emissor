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


class Preprocessor:




class ModalitySetup:
    def __init__(self, dataset, modality: Modality):
        self._storage = ScenarioStorage(dataset)
        self._modality = modality

    def run_setup(self):
        for scenario_id in self.list_scenarios():
            try:
                self.create_modality(scenario_id)
            except ValueError:
                logging.exception("Modality %s could not be created for scenario %s", modality, scenario_id)

    def list_scenarios(self) -> Iterable[str]:
        return self._storage.list_scenarios()

    def create_modality(self, scenario_id: str) -> Iterable[Signal[Any, Any]]:
        signals = self._storage.load_modality(scenario_id, self._modality)
        if signals is None:
            signals = self._create_modality_metadata(scenario_id, self._modality)
            self._storage.save_signals(scenario_id, self._modality, signals)

        return signals

    def _create_modality_metadata(self, scenario_id) -> Iterable[Signal[Any, Any]]:
        scenario = self.create_scenario(scenario_id)
        if self._modality == Modality.IMAGE:
            image_meta = self._storage.load_images(self._storage.load_scenario(scenario_id))
            return [self._create_image_signal(scenario, meta) for _, meta in image_meta.iterrows()]
        elif self._modality == Modality.TEXT:
            texts = self._storage.load_text(scenario_id)
            return [self._create_text_signal(scenario, utt) for _, utt in texts.iterrows()]
        else:
            raise ValueError("Unsupported modality " + modality.name)

    def save_signal(self, scenario_id: str, signal: Signal[Any, Any]) -> None:
        self._storage.save_signal(scenario_id, signal)

    def _create_image_signal(self, scenario: Scenario, image_meta: Series) -> ImageSignal:
        bounds = image_meta['bounds']
        image_time = image_meta['time']
        file = image_meta['file']
        image_signal = ImageSignal.for_scenario(scenario.id, image_time, image_time, file, bounds)

        return image_signal

    def _create_text_signal(self, scenario: Scenario, utterance_data: Series):
        timestamp = utterance_data['time'] if 'time' in utterance_data else scenario.start
        utterance = utterance_data['utterance']
        signal = TextSignal.for_scenario(scenario.id, timestamp, timestamp, utterance_data['file'], utterance, [])

        return signal


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup EMISSOR metadata for a dataset.')
    parser.add_argument('--dataset', type=str,
                        help="Base directory that contains the scenarios of the dataset.")

    args = parser.parse_args()
    logging.info("Setting up EMISSOR for dataset %s", args.dataset)

    ModalitySetup(args.dataset)