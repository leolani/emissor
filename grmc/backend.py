import os
from glob import glob
from typing import Iterable

import jsonpickle
import pandas as pd
import sys
import time
import uuid
from PIL import Image

from grmc.cache import ScenarioCache
from grmc.representation.container import TemporalRuler
from grmc.representation.entity import Person, Gender
from grmc.representation.scenario import Scenario, ScenarioContext, Modality, ImageSignal, TextSignal, Mention, \
    Annotation

jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
jsonpickle.set_preferred_backend('simplejson')

base_path = sys.argv[0]

_SPEAKER = Person(uuid.uuid4(), "Speaker", 50, Gender.UNDEFINED)
_DEFAULT_SIGNALS = {
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
}


def _get_base():
    return "webapp/src/assets"


def _get_path(scenario_name, modality: str = None, file: str = None, extension=".json"):
    path = os.path.join(_get_base(), scenario_name)
    if modality:
        path = os.path.join(path, modality)
    else:
        path = os.path.join(path, scenario_name)

    if file:
        path = os.path.join(path, file)

    return path + extension if extension else path


def _guess_timestamp(name: str, scenario_start: int, scenario_end: int) -> int:
    try:
        file_timestamp = int(name.split('_')[-1])
        if scenario_start < file_timestamp < scenario_end:
            return file_timestamp
    except ValueError:
        pass

    return scenario_start


def _get_start_ruler(scenario_meta):
    return TemporalRuler(scenario_meta.id, scenario_meta.start, scenario_meta.start)


def _load_image(image, scenario_meta):
    file_name = os.path.basename(image)
    path = Modality.IMAGE.name.lower() + "/" + file_name
    name = os.path.splitext(file_name)[0]

    timestamp = _guess_timestamp(name, scenario_meta.start, scenario_meta.end)

    with Image.open(_get_path(scenario_meta.id, Modality.IMAGE.name.lower(), file_name, extension=None)) as img:
        bounds = (0, 0) + img.size

    image_signal = ImageSignal.for_scenario(scenario_meta.id, timestamp, timestamp, path, bounds)
    display_annotation = Annotation(name, "annotation_tool", int(time.time()))
    display = Mention([image_signal.ruler.get_area_bounding_box(*bounds)], [display_annotation])
    image_signal.mentions.append(display)

    return image_signal


def _create_text_signal(utt, scenario_meta: Scenario, file: str, idx: int):
    timestamp = utt['time'] if 'time' in utt else scenario_meta.start
    file_idx = file #+ "#" + str(idx)

    mentions = []

    return TextSignal.for_scenario(scenario_meta.id, timestamp, timestamp, file_idx, utt['utterance'], mentions)


def _guess_scenario_range(scenario_id: str, modalities: Iterable[str]):
    min_ = 60 * 60 * 24 * 365 * 100
    max_ = 0

    if Modality.IMAGE.name.lower() in modalities:
        image_path = _get_path(scenario_id, Modality.IMAGE.name.lower(), extension=None)
        for image in glob(os.path.join(image_path, "*")):
            image_name = os.path.splitext(os.path.basename(image))[0]
            image_timestamp = _guess_timestamp(image_name, 0, 60 * 60 * 24 * 365 * 100)
            if image_timestamp and image_timestamp < min_:
                min_ = image_timestamp
            if image_timestamp and image_timestamp > max_:
                max_ = image_timestamp

    if Modality.TEXT.name.lower() in modalities:
        text_path = _get_path(scenario_id, Modality.TEXT.name.lower(), extension=None)
        csv_files = glob(os.path.join(text_path, "*.csv"))
        if len(csv_files):
            timestamps = pd.concat([pd.read_csv(f, skipinitialspace=True) for f in csv_files])['time']
            min_ = min(min_, timestamps.min())
            max_ = max(max_, timestamps.max())

    return int(min(min_, max_)), int(max_)


class Backend:
    def __init__(self):
        self._cache = None

    def list_scenarios(self):
        return tuple(os.path.basename(path[:-1]) for path in glob(os.path.join(_get_base(), "*", "")))

    def load_scenario(self, scenario_id):
        scenario_path = _get_path(scenario_id)
        self._ensure_scenario(scenario_id, scenario_path)
        with open(scenario_path) as json_file:
            json_string = json_file.read()
            scenario = jsonpickle.decode(json_string)

        self._cache = ScenarioCache()

        return scenario

    def _ensure_scenario(self, scenario_id, scenario_meta_path):
        if not os.path.isfile(scenario_meta_path):
            start, end = _guess_scenario_range(scenario_id, _DEFAULT_SIGNALS.keys())

            scenario_id = Scenario.new_instance(scenario_id, start, end,
                                                ScenarioContext("robot_agent", _SPEAKER, [], []),
                                                _DEFAULT_SIGNALS)
            with open(scenario_meta_path, 'w') as json_file:
                json_string = jsonpickle.encode(scenario_id, make_refs=False)
                json_file.write(json_string)

    def load_modality(self, scenario_id, modality):
        # if modality in self._cache:
        #     return self._cache[modality].values()

        modality_meta_path = _get_path(scenario_id, modality)
        self._ensure_modality_metadata(modality_meta_path, scenario_id, modality)
        with open(modality_meta_path) as json_file:
            signals = jsonpickle.decode(json_file.read())

        self._cache[modality] = signals

        return signals

    def _ensure_modality_metadata(self, modality_meta_path, scenario, modality):
        scenario_meta = self.load_scenario(scenario)
        if modality.lower() == "image":
            image_path = _get_path(scenario, modality, extension=None)
            images = glob(os.path.join(image_path, "*"))
            signals = [_load_image(image, scenario_meta) for image in images]
        elif modality.lower() == "text":
            text_path = _get_path(scenario, modality, extension=None)
            csv_files = glob(os.path.join(text_path, "*.csv"))

            signals = []
            for idx, file in enumerate(csv_files):
                utterances = pd.read_csv(file, quotechar='"', sep=',', skipinitialspace=True)
                signals += [_create_text_signal(utt, scenario_meta, file, idx) for _, utt in utterances.iterrows()]
        else:
            raise ValueError("Unsupported modality " + modality)

        if not os.path.isfile(modality_meta_path):
            with open(modality_meta_path, 'w') as json_file:
                json_file.write(jsonpickle.encode(signals, make_refs=False))

    def save_signal(self, name, signal):
        self._cache[signal.modality][signal.id] = signal
        with open(_get_path(name, signal.modality), 'w') as json_file:
            json_file.write(jsonpickle.encode(self._cache[signal.modality].values(), make_refs=False))
