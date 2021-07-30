from glob import glob

import os
from types import MappingProxyType
from typing import Iterable, Optional, Any, Union, Mapping, Dict, Tuple

from emissor.representation.scenario import Scenario, Modality, Signal, ImageSignal, TextSignal, ScenarioContext
from emissor.representation.util import unmarshal, marshal

ANNOTATION_TOOL_ID = "annotation_tool"


DEFAULT_SIGNAL_PATHS = MappingProxyType({
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
})


def file_name(path):
    return os.path.splitext(base_name(path))[0]


def base_name(path):
    return os.path.basename(path)


class ScenarioController:
    def __init__(self, scenario: Scenario, storage):
        self._storage = storage
        self._scenario = scenario
        self._signals = dict()

    def append_signal(self, signal: Signal[Any, Any]):
        if signal.modality not in self._signals:
            self.load_signals((signal.modality,))

        self._signals[signal.modality].append(signal)

    @property
    def id(self) -> str:
        return self.scenario.id

    @property
    def scenario(self) -> Scenario:
        return self._scenario

    @property
    def signals(self) -> Mapping[Modality, Iterable[Signal[Any, Any]]]:
        return dict(self._signals)

    def load_signals(self, modalities: Tuple[Modality]):
        for modality in modalities:
            signals = self._storage.load_modality(self.scenario.id, modality)
            signals = signals if signals else []
            self._signals[modality] = signals

    def get_signals(self, modality: Modality) -> Iterable[Signal[Any, Any]]:
        if modality not in self._signals:
            self.load_signals((modality,))

        return list(self._signals[modality])


class ScenarioStorage:
    EXTENSION = ".json"

    def __init__(self, data_path):
        self._data_path = data_path

    @property
    def base_path(self):
        return self._data_path

    def list_scenarios(self) -> Iterable[str]:
        return tuple(os.path.basename(path[:-1]) for path in glob(os.path.join(self.base_path, "*", "")))

    def create_scenario(self, scenario_id: str, start: int, end: int, context: ScenarioContext,
                     signals: Dict[str, str] = DEFAULT_SIGNAL_PATHS) -> ScenarioController:
        scenario = Scenario.new_instance(scenario_id, start, end, context, signals)
        metadata_path = self._get_scenario_metadata_path(scenario_id)
        with open(metadata_path, 'w') as json_file:
            json_file.write(marshal(scenario, cls=Scenario))

        return ScenarioController(scenario, self)

    def load_scenario(self, scenario_id: str) -> Optional[ScenarioController]:
        scenario_path = self._get_scenario_metadata_path(scenario_id)
        if not os.path.isfile(scenario_path):
            raise ValueError(f"No scenario with id {scenario_id} at {scenario_path}")

        with open(scenario_path) as json_file:
            json_string = json_file.read()
        scenario = unmarshal(json_string, cls=Scenario)

        return ScenarioController(scenario, self)

    def save_scenario(self, scenario: ScenarioController) -> None:
        if not isinstance(scenario, ScenarioController):
            raise ValueError("Can only save ScenarioController instances, got: " + type(scenario) + ". See the #create_scenario method.")

        scenario_metadata_path = self._get_scenario_metadata_path(scenario.id)

        plain_scenario = scenario.scenario
        with open(scenario_metadata_path, 'w') as json_file:
            json_file.write(marshal(plain_scenario, cls=Scenario))

        for modality, signals in scenario.signals.items():
            self._save_signals(self._get_metadata_path(plain_scenario, modality), signals, modality)

    def _save_signals(self, path, signals, modality: Modality):
        if modality == Modality.IMAGE:
            cls = ImageSignal
        elif modality == Modality.TEXT:
            cls = TextSignal
        else:
            raise ValueError(f"Unsupported modality: {modality}")

        with open(path, 'w') as json_file:
            json_file.write(marshal(signals, cls=cls))

    def load_modality(self, scenario_id: str, modality: Modality) -> Optional[Iterable[Signal[Any, Any]]]:
        scenario = self.load_scenario(scenario_id)
        modality_meta_path = self._get_metadata_path(scenario.scenario, modality)
        if not modality_meta_path or not os.path.isfile(modality_meta_path):
            return None

        with open(modality_meta_path) as json_file:
            if modality == Modality.IMAGE:
                cls = ImageSignal
            elif modality == Modality.TEXT:
                cls = TextSignal
            else:
                raise ValueError(f"Unsupported modality: {modality}")

            return unmarshal(json_file.read(), cls=cls)

    def _get_scenario_metadata_path(self, scenario_id):
        return os.path.join(self.base_path, scenario_id, scenario_id + self.EXTENSION)

    def _get_metadata_path(self, scenario: Scenario, modality: Union[Modality, str]):
        scenario_path = os.path.join(self.base_path, scenario.id)

        modality_key = modality if isinstance(modality, str) else modality.name.lower()
        if modality_key not in scenario.signals:
            return None

        relative_path = scenario.signals[modality_key]

        return os.path.join(scenario_path, relative_path)
