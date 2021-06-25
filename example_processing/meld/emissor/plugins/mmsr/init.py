from glob import glob

import datetime
import json
import logging
import os
import pandas as pd
import re
from typing import Mapping

from emissor.persistence import ScenarioStorage
from emissor.processing.api import ScenarioInitializer
from emissor.representation.scenario import Scenario, Modality, ImageSignal, TextSignal
from example_processing.meld.meld import MELDScenarioContext

_MAX_GUESS_RANGE = 1000 * 60 * 60 * 24 * 365 * 100

_MELD_SIGNALS = {
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
}

_DEFAULT_MODALITIES = (Modality.TEXT, Modality.IMAGE)


logger = logging.getLogger(__name__)


class MMSRMeldInitializer(ScenarioInitializer):
    def __init__(self, dataset):
        self.dataset = dataset
        self.processing_dir = os.path.join(self.dataset, "processing", "frames")
        self.current_scenario = None
        self.processing_meta = None

    @property
    def parallel(self) -> bool:
        return True

    def initialize_scenario(self, scenario_id: str, storage: ScenarioStorage):
        self.current_scenario = scenario_id
        self.processing_meta = self.load_processing_metadata(scenario_id, storage)

        scenario = self.create_scenario_metadata(scenario_id)
        storage.save_scenario(scenario)

        logger.info("Initialized scenario %s", scenario_id)

    def create_scenario_metadata(self, scenario_id: str) -> Scenario:
        start, end = self.processing_meta.start.min(), self.processing_meta.start.max()

        dialog_info = self.processing_meta[['season', 'episode', 'dialog_id']].drop_duplicates()
        if not len(dialog_info) == 1:
            raise ValueError(f"Inconsistent dialog information: {dialog_info.tostring()} for scenario {scenario_id}")

        season, episode, dialog_id = dialog_info.iloc[0]
        speakers = self.processing_meta['speaker'].unique()

        return Scenario.new_instance(scenario_id, start, end,
                                     MELDScenarioContext(None, season, episode, dialog_id, speakers),
                                     _MELD_SIGNALS)

    def initialize_modality(self, modality: Modality, scenario: Scenario, storage: ScenarioStorage):
        self.ensure_scenario(scenario.id)

        if modality not in [Modality.TEXT, Modality.IMAGE]:
             return

        if modality == Modality.IMAGE:
            signals = [self.create_image_signal(scenario, meta) for _, meta in self.processing_meta.iterrows()]
        else:
            text_entries = self.processing_meta.groupby(['dialog_id', 'utterance_id']).first()
            signals = [self.create_text_signal(scenario, utt) for idx, utt in text_entries.iterrows()]

        storage.save_signals(scenario.id, modality, signals)

    def create_text_signal(self, scenario: Scenario, text_meta: pd.DataFrame) -> TextSignal:
        return TextSignal.for_scenario(scenario.id, text_meta.start, text_meta.end, text_meta.file_text, text_meta.utterance, [])

    def create_image_signal(self, scenario: Scenario, image_meta: pd.DataFrame) -> ImageSignal:
        bounds = (0, 0, image_meta.width, image_meta.height)
        image_start = image_meta.frame_start
        image_end = image_meta.frame_end
        file = image_meta.file_image

        return ImageSignal.for_scenario(scenario.id, image_start, image_end, file, bounds)

    def load_processing_metadata(self, scenario_id: str, storage: ScenarioStorage) -> pd.DataFrame:
        text_metadata = self.load_text(scenario_id, storage)
        image_metadata = self.load_image_metadata(scenario_id, storage)

        metadata = pd.merge(image_metadata, text_metadata, on=['dialog_id', 'utterance_id'], suffixes=('_image', '_text'))
        metadata["frame_start"] = metadata["start"] + (metadata["frame_idx"] / metadata['fps_original'] * 1000.0).round()
        metadata["frame_end"] = metadata["start"] + (1000.0 / metadata['fps_original']).round()

        return metadata

    def load_text(self, scenario_id: str, storage: ScenarioStorage) -> Mapping:
        text_path = os.path.join(storage.base_path, scenario_id, Modality.TEXT.name.lower())
        json_files = tuple(glob(os.path.join(text_path, "*.json")))

        return pd.DataFrame.from_records(self.load_json(file) for file in json_files)

    def load_json(self, file):
        with open(file, 'r') as f:
            data = json.load(f)

        data['file'] = Modality.TEXT.name.lower() + "/" + os.path.basename(file)
        data['start'] = self.to_millisec(data['StartTime'])
        data['end'] = self.to_millisec(data['EndTime'])
        data = {key.lower(): val for key, val in data.items()}
        data['dialog_id'] = int(data['dialogue_id'])
        del data['dialogue_id']
        data['utterance_id'] = int(data['utterance_id'])

        return data

    def load_image_metadata(self, scenario_id, storage):
        image_path = os.path.join(storage.base_path, scenario_id, Modality.IMAGE.name.lower())
        images = pd.DataFrame.from_records(self.ids_from_name(image, scenario_id, storage)
                                           for image in glob(os.path.join(image_path, "*")))

        scenario_frames_path = os.path.join(self.processing_dir, scenario_id)
        frame_metadata = pd.DataFrame.from_records(self.load_frame_metadata(path, scenario_id, storage)
                                                   for path in glob(os.path.join(scenario_frames_path, "*")))

        return pd.merge(images, frame_metadata, on=['dialog_id', 'utterance_id'])

    def load_frame_metadata(self, metadata_path: str, scenario_id, storage: ScenarioStorage) -> dict:
        with open(metadata_path, 'r') as file:
            metadata = json.load(file)

        ids = self.ids_from_name(metadata_path, scenario_id, storage)
        metadata['dialog_id'] = ids['dialog_id']
        metadata['utterance_id'] = ids['utterance_id']

        return metadata

    def ids_from_name(self, metadata_path, scenario_id, storage: ScenarioStorage):
        base = os.path.basename(metadata_path)
        name = os.path.splitext(os.path.basename(base))[0]
        ids = [int(id) for id in re.sub("[A-Za-z]", "", name).split("_")]

        if len(ids) == 2:
            ids.append(-1)
        if len(ids) != 3:
            raise ValueError(f"Invalid name {metadata_path}")

        dialog_id, utterance_id, frame_idx = ids

        file_path = os.path.relpath(os.path.abspath(metadata_path), os.path.join(storage.base_path, scenario_id))

        return {'file': file_path, 'dialog_id': dialog_id, 'utterance_id': utterance_id, 'frame_idx': frame_idx}

    def to_millisec(self, time_str):
        return int(1000 * (datetime.datetime.strptime(time_str, '%H:%M:%S,%f').timestamp()
                           - datetime.datetime(1900, 1, 1).timestamp()))

    def ensure_scenario(self, scenario_id):
        if not self.current_scenario == scenario_id:
            raise ValueError(f"Invalid scenario_id: {scenario_id}")