import os
import time
import uuid
from typing import Iterable, Any, Dict

from emissor.annotation.brain.util import EmissorBrain
from emissor.annotation.default_plugin import AnnotationToolProcessorPlugin
from emissor.persistence import ScenarioStorage
from emissor.persistence.persistence import ScenarioController
from emissor.processing.util import discover_plugins, from_plugins
from emissor.representation.annotation import Triple, Entity, EntityType
from emissor.representation.container import MultiIndex, Index, AtomicRuler, Ruler
from emissor.representation.entity import Person, Gender, Emotion
from emissor.representation.scenario import Scenario, Modality, Mention, \
    Annotation, Signal

# TODO Put to a central place
ANNOTATION_TOOL_ID = "annotation tool"
_SPEAKER = Person(str(uuid.uuid4()), "Speaker", 50, Gender.UNDEFINED)
_DEFAULT_SIGNALS = {
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
}


class Backend:
    def __init__(self, data_path, plugins):
        plugins = discover_plugins(os.path.abspath(plugin) for plugin in plugins)
        if not plugins:
            plugins = [AnnotationToolProcessorPlugin()]
        self._data_processing = from_plugins(plugins, data_path, preprocessing=False, init=True, processors=[], num_jobs=1)

        self._storage = ScenarioStorage(data_path)

        self._scenario_ctrl: ScenarioController = None
        self._scenario_brain: EmissorBrain = None

    def list_scenarios(self) -> Iterable[str]:
        return self._storage.list_scenarios()

    def _load_scenario_ctrl(self, scenario_id: str) -> ScenarioController:
        if not self._scenario_ctrl or self._scenario_ctrl.id != scenario_id:
            try:
                self._scenario_ctrl = self._storage.load_scenario(scenario_id)
            except ValueError:
                self._data_processing.run_init()
                self._scenario_ctrl = self._storage.load_scenario(scenario_id)

        return self._scenario_ctrl

    def load_scenario(self, scenario_id: str) -> Scenario:
        return self._load_scenario_ctrl(scenario_id).scenario

    def load_modality(self, scenario_id: str, modality: Modality) -> Iterable[Signal[Any, Any]]:
        ctrl = self._load_scenario_ctrl(scenario_id)
        ctrl.load_signals(modalities=[modality])

        return ctrl.signals[modality]

    def load_signal(self, scenario_id: str, modality: Modality, signal_id: str) -> Signal[Any, Any]:
        for signal in self.load_modality(scenario_id, modality):
            if signal.id == signal_id:
                return signal

        return None

    def save_signal(self, scenario_id: str, signal: Signal[Any, Any]) -> None:
        scenario_ctrl = self._load_scenario_ctrl(scenario_id)
        scenario_ctrl.append_signal(signal)
        self._storage.save_scenario(scenario_ctrl)

    def create_mention(self, scenario_id: str, modality: Modality, signal_id: str):
        return Mention(str(uuid.uuid4()), [], [])

    def create_annotation(self, type_: str):
        if type_.lower() == "person":
            value = Person(str(uuid.uuid4()), "", 0, Gender.UNDEFINED)
        elif type_.lower() == "display":
            value = "new"
        elif type_.lower() == "pos":
            value = "POS-TAG"
        elif type_.lower() == "emotion":
            value = Emotion.NEUTRAL.name.lower()
        elif type_.lower() == "triple":
            value = Triple(Entity("", EntityType.PERSON), "", Entity("", EntityType.PERSON))
        else:
            raise ValueError("Unsupported annotation type: " + type_)

        return Annotation(type_, value, "", int(time.time()))

    def create_segment(self, scenario_id, modality, signal_id, mention_id: str, type_: str, container_id: str) -> Ruler:
        signal = self.load_signal(scenario_id, modality, signal_id)

        container_id = container_id if container_id else signal.id
        if type_.lower() == "multiindex":
            return MultiIndex(container_id, signal.ruler.bounds)
        if type_.lower() == "index":
            return Index(container_id, signal.ruler.start, signal.ruler.stop)
        if type_.lower() == "atomic":
            return AtomicRuler(container_id)

        raise ValueError("Unsupported type: " + type_.lower())

    def _get_brain(self):
        if not self._scenario_ctrl:
            return None

        if self._scenario_brain and self._scenario_brain.scenario_id == self._scenario_ctrl.id:
            return self._scenario_brain.s

        ememory_path = os.path.join(self._storage.base_path, self._scenario_ctrl.id, 'rdf', 'episodic_memory')
        self._scenario_brain = EmissorBrain(ememory_path, self._scenario_ctrl.id)

        return self._scenario_brain

    def load_annotation_types(self) -> Iterable[Dict]:
        return self._get_brain().get_annotation_types()

    def load_relation_types(self) -> Iterable[Dict]:
        return self._get_brain().get_relation_types()

    def load_instances_of_type(self, class_type: str) -> Iterable[Dict]:
        return self._get_brain().get_instances_of_type(class_type)

    def create_denotations(self, scenario_id: str, modality: str, signal_id: str, mention_id: str,
                           annotation_id: str) -> Dict:

        # Load modality data
        signals = self.load_modality(scenario_id, Modality[modality.upper()])

        # Filter signals to get the right one
        signals = [sig for sig in signals if sig.id == signal_id]
        signal = signals[0]

        # Filter mentions to get the right one
        mentions = [men for men in signal.mentions if men.id == mention_id]
        mention = mentions[0]

        # Filter annotations to get the right one
        annotations = [ann for ann in mention.annotations if ann.value.id == annotation_id]
        annotation = annotations[0]

        # Create triple
        triples = self._get_brain().denote_things(mention, annotation)

        return {"triples": triples}
