from glob import glob

import datetime
import json
import logging
import os
import pandas as pd
from PIL import Image
from pandas import DataFrame
from typing import Iterable, Optional, Any, Tuple, Union

from emissor.annotation.brain.util import EmissorBrain
from emissor.annotation.cache import ScenarioCache
from emissor.representation.scenario import Scenario, Modality, Signal, ImageSignal, TextSignal
from emissor.representation.util import unmarshal, marshal

logger = logging.getLogger(__name__)


ANNOTATION_TOOL_ID = "annotation_tool"

_MAX_GUESS_RANGE = 1000 * 60 * 60 * 24 * 365 * 100


def file_name(path):
    return os.path.splitext(base_name(path))[0]


def base_name(path):
    return os.path.basename(path)


class ScenarioStorage:
    def __init__(self, data_path, mode="filename"):
        self._cache = None
        self.brain = None
        self._data_path = data_path
        self._mode = mode

    @property
    def base_path(self):
        return self._data_path

    def _get_path(self, scenario_name, modality: Optional[Union[Modality, str]] = None, file: str = None,
                  extension: Optional[str] = ".json"):
        path = os.path.join(self.base_path, scenario_name)
        if modality:
            path = os.path.join(path, modality if isinstance(modality, str) else modality.name.lower())
        else:
            path = os.path.join(path, scenario_name)

        if file:
            path = os.path.join(path, file)

        return path + extension if extension else path

    def load_text(self, scenario_id: str) -> DataFrame:
        text_path = self._get_path(scenario_id, Modality.TEXT, extension=None)
        csv_files = tuple(glob(os.path.join(text_path, "*.csv")))

        text_df = pd.concat(self._load_csv(file) for file in csv_files) if csv_files else pd.DataFrame()
        text_data = text_df.to_dict('records')
        # text_data = [row for row in tuple(zip(*text_df.iterrows()))[1]] \
        #        if csv_files else []

        json_files = tuple(glob(os.path.join(text_path, "*.json")))
        text_data += [self._load_json(file) for file in json_files]

        return text_data

    def _load_csv(self, file):
        data = pd.read_csv(file, skipinitialspace=True)
        data['chat'] = file_name(file)
        data['file'] = Modality.TEXT.name.lower() + "/" + base_name(file) + "#"
        data['file'] = data['file'] + data.index.astype(str)

        return data

    def _load_json(self, file):
        with open(file, 'r') as f:
            data = json.load(f)
        data['speaker'] = data['Speaker']
        data['utterance'] = data['Utterance']
        data['chat'] = data['Dialogue_ID']
        data['file'] = Modality.TEXT.name.lower() + "/" + base_name(file)
        data['start'] = self._to_millisec(data['StartTime'])
        data['end'] = self._to_millisec(data['EndTime'])

        return data

    def load_images(self, scenario: Scenario) -> DataFrame:
        image_path = self._get_path(scenario.id, Modality.IMAGE, extension=None)
        images = glob(os.path.join(image_path, "*"))

        return pd.DataFrame([self.get_image_meta(image, scenario) for image in images],
                            columns=["file", "time", "bounds"])

    def get_image_meta(self, image: str, scenario: Scenario) -> Tuple[int, Tuple[int, int, int, int]]:
        base = base_name(image)
        name = file_name(base)
        # Path in file system
        image_path = self._get_path(scenario.id, Modality.IMAGE, base, extension=None)
        # Path in scenario
        image_file = Modality.IMAGE.name.lower() + "/" + base

        timestamp = self._guess_timestamp(name, scenario.id, scenario.start, scenario.end)

        if not os.path.isfile(image_path):
            return None

        with Image.open(image_path) as img:
            bounds = (0, 0) + img.size

        return image_file, timestamp, bounds

    def guess_scenario_range(self, scenario_id: str, modalities: Iterable[str]):
        min_ = _MAX_GUESS_RANGE
        max_ = 0

        if Modality.IMAGE.name.lower() in modalities:
            if self._mode == "filename":
                image_path = self._get_path(scenario_id, Modality.IMAGE, extension=None)
                for image in glob(os.path.join(image_path, "*")):
                    image_name = os.path.splitext(os.path.basename(image))[0]
                    image_timestamp = self._guess_timestamp(image_name, scenario_id, min_, max_)
                    if image_timestamp and image_timestamp < min_:
                        min_ = image_timestamp
                    if image_timestamp and image_timestamp > max_:
                        max_ = image_timestamp
            elif self._mode == "metadata":
                pass
            else:
                raise ValueError("Unknown mode: " + self._mode)

        if Modality.TEXT.name.lower() in modalities:
            ranges = [(text['start'], text['end'])
                      for text in self.load_text(scenario_id) if 'start' in text and 'end' in text]
            ranges += [(int(text['time']),) for text in self.load_text(scenario_id) if 'time' in text]
            timestamps = [t for range in ranges for t in range]

            min_ = min(min_, min(timestamps) if timestamps else 0)
            max_ = max(max_, max(timestamps) if timestamps else 0)

        return int(min(min_, max_)), int(max_)

    def _guess_timestamp(self, name: str, scenario_id: str, scenario_start: int, scenario_end: int) -> int:
        file_timestamp = scenario_start

        try:
            if self._mode == "filename":
                file_timestamp = int(name.split('_')[-1])
            elif self._mode == "metadata":
                parts = name.split('_')
                metadata = self._load_image_metadata(scenario_id, "_".join(parts[:-1]))
                frame_idx = int(parts[-1])
                frame_length = 1 / metadata["fps_original"]
                file_timestamp = frame_idx * frame_length
            else:
                raise NotImplementedError("Unknown mode: " + self._mode)
        except ValueError:
            pass

        if scenario_start <= file_timestamp < scenario_end:
            return file_timestamp

        return scenario_start

    def _to_millisec(self, time_str):
        return int(1000 * (datetime.datetime.strptime(time_str, '%H:%M:%S,%f').timestamp()
                           - datetime.datetime(1900, 1, 1).timestamp()))

    def _load_image_metadata(self, scenario_id: str, name: str) -> dict:
        metadata_path = os.path.join(self._data_path, "..", "processing", "frames", f"{scenario_id}/{name}.json")
        with open(metadata_path, 'r') as file:
            metadata = json.load(file)

        return metadata

    def list_scenarios(self) -> Tuple[str]:
        return tuple(os.path.basename(path[:-1]) for path in glob(os.path.join(self.base_path, "*", "")))

    def load_scenario(self, scenario_id: str) -> Optional[Scenario]:
        scenario_path = self._get_path(scenario_id)
        if not os.path.isfile(scenario_path):
            return None

        with open(scenario_path) as json_file:
            json_string = json_file.read()
        scenario = unmarshal(json_string)

        self._cache = ScenarioCache(scenario_id)

        # Load memories
        ememory_path = self._get_path(scenario_id, 'rdf', 'episodic_memory', extension=None)
        self.brain = EmissorBrain(ememory_path)

        return scenario

    def save_scenario(self, scenario: Scenario) -> None:
        with open(self._get_path(scenario.id), 'w') as json_file:
            json_file.write(marshal(scenario))

    def load_modality(self, scenario_id: str, modality: Modality) -> Optional[Iterable[Signal[Any, Any]]]:
        if not self._cache or self._cache.scenario_id != scenario_id:
            self.load_scenario(scenario_id)

        if self._cache and modality in self._cache:
            return self._cache[modality].values()

        modality_meta_path = self._get_path(scenario_id, modality)
        if not os.path.isfile(modality_meta_path):
            logger.warning("%s modality metadata (%s) for scenario %s not present",
                           modality.name, modality_meta_path, scenario_id)
            return None

        with open(modality_meta_path) as json_file:
            if modality == Modality.IMAGE:
                cls = ImageSignal
            elif modality == Modality.TEXT:
                cls = TextSignal
            else:
                raise ValueError(f"Unsupported modality: {modality}")

            signals = unmarshal(json_file.read())

        self._cache[modality] = signals

        return signals

    def load_signal(self, scenario_id: str, modality: Modality, signal_id: str) -> Signal[Any, Any]:
        if modality not in self._cache:
            self.load_modality(scenario_id, modality)

        return self._cache[modality][signal_id]

    def save_signals(self, scenario_id: str, modality: Modality, signals: Iterable[Signal[Any, Any]]) -> None:
        self._cache[modality] = signals
        self._save_signals(self._get_path(scenario_id, modality), signals, modality)

    def save_signal(self, scenario_id: str, signal: Signal[Any, Any]) -> None:
        modality = signal.modality if isinstance(signal.modality, Modality) else Modality[signal.modality.upper()]
        self._cache[modality][signal.id] = signal
        self._save_signals(self._get_path(scenario_id, modality), self._cache[modality].values(), modality)

    def _save_signals(self, path, signals, modality: Modality):
        if modality == Modality.IMAGE:
            cls = ImageSignal
        elif modality == Modality.TEXT:
            cls = TextSignal
        else:
            raise ValueError(f"Unsupported modality: {modality}")

        with open(path, 'w') as json_file:
            json_file.write(marshal(signals))
