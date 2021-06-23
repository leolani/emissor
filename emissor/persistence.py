from glob import glob

import os
from typing import Iterable, Optional, Any, Union

from emissor.annotation.brain.util import EmissorBrain
from emissor.representation.scenario import Scenario, Modality, Signal, ImageSignal, TextSignal
from emissor.representation.util import unmarshal, marshal, Identifier

ANNOTATION_TOOL_ID = "annotation_tool"

_MAX_GUESS_RANGE = 1000 * 60 * 60 * 24 * 365 * 100


def file_name(path):
    return os.path.splitext(base_name(path))[0]


def base_name(path):
    return os.path.basename(path)


class _ScenarioCache(dict):
    def __init__(self, scenario: Scenario) -> None:
        self._scenario_id = scenario.id
        self._entity_cache = dict()
        self._entity_cache[scenario.id] = scenario

    @property
    def scenario_id(self):
        return self._scenario_id

    def __setitem__(self, key: Modality, value: Iterable[Signal]):
        super().__setitem__(key, {signal.id: signal for signal in value})

        # Entities are:
        #  * Scenario
        #  * Containers: Signal, Annotation values
        #  * Mentions
        self._entity_cache.update(self[key])
        self._entity_cache.update({mention.id: mention
                                   for signal in self[key].values()
                                   for mention in signal.mentions})
        self._entity_cache.update({annotation.value.id: annotation.value
                                   for signal in self[key].values()
                                   for mention in signal.mentions
                                   for annotation in mention.annotations if hasattr(annotation.value, "id")})

    def get_entity(self, id: Identifier):
        return self._entity_cache[id] if id in self._entity_cache else None


class ScenarioStorage:
    EXTENSION = ".json"

    def __init__(self, data_path):
        self._cache = None
        self.brain = None
        self._data_path = data_path

    @property
    def base_path(self):
        return self._data_path

    def _get_path(self, scenario_id, modality: Optional[Union[Modality, str]] = None):
        if not modality:
            return os.path.join(self.base_path, scenario_id)

        scenario = self.load_scenario(scenario_id)
        modality_key = modality if isinstance(modality, str) else modality.name.lower()
        if modality_key not in scenario.signals:
            return None

        scenario_path = self._get_path(scenario_id)
        relative_path = scenario.signals[modality_key]

        return os.path.join(scenario_path, relative_path)

    def list_scenarios(self) -> Iterable[str]:
        return tuple(os.path.basename(path[:-1]) for path in glob(os.path.join(self.base_path, "*", "")))

    def load_scenario(self, scenario_id: str) -> Optional[Scenario]:
        scenario_path = os.path.join(self._get_path(scenario_id), scenario_id + self.EXTENSION)
        if not os.path.isfile(scenario_path):
            raise ValueError(f"No scenario with id {scenario_id} at {scenario_path}")

        with open(scenario_path) as json_file:
            json_string = json_file.read()
        scenario = unmarshal(json_string, cls=Scenario)

        self._cache = _ScenarioCache(scenario)

        # Load memories
        ememory_path = os.path.join(self._get_path(scenario_id), 'rdf', 'episodic_memory')
        self.brain = EmissorBrain(ememory_path)

        return scenario

    def save_scenario(self, scenario: Scenario) -> None:
        scenario_metadata_path = os.path.join(self._get_path(scenario.id), scenario.id + self.EXTENSION)
        with open(scenario_metadata_path, 'w') as json_file:
            json_file.write(marshal(scenario, cls=Scenario))

    def load_modality(self, scenario_id: str, modality: Modality) -> Optional[Iterable[Signal[Any, Any]]]:
        if not self._cache or self._cache.scenario_id != scenario_id:
            self.load_scenario(scenario_id)

        if self._cache and modality in self._cache:
            return self._cache[modality].values()

        modality_meta_path = self._get_path(scenario_id, modality)
        if not modality_meta_path or not os.path.isfile(modality_meta_path):
            return None

        with open(modality_meta_path + self.EXTENSION) as json_file:
            if modality == Modality.IMAGE:
                cls = ImageSignal
            elif modality == Modality.TEXT:
                cls = TextSignal
            else:
                raise ValueError(f"Unsupported modality: {modality}")

            signals = unmarshal(json_file.read(), cls=cls)

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
            json_file.write(marshal(signals, cls=cls))

    def get_entity(self, id: Identifier):
        if not self._cache:
            raise ValueError("No scenario loaded")

        return self._cache.get_entity(id)