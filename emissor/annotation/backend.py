import time
import uuid
from typing import Iterable, Any, Dict

from nltk import TreebankWordTokenizer
from pandas import Series

from emissor.annotation.persistence import ScenarioStorage, ANNOTATION_TOOL_ID, file_name
from emissor.representation.annotation import AnnotationType, Token, Triple, Entity, EntityType
from emissor.representation.container import TemporalRuler, MultiIndex, Index, AtomicRuler, Ruler
from emissor.representation.entity import Person, Gender, Emotion
from emissor.representation.scenario import Scenario, ScenarioContext, Modality, ImageSignal, TextSignal, Mention, \
    Annotation, Signal
from emissor.representation.util import marshal

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
    display = Mention(str(uuid.uuid4()), [image_signal.ruler.get_area_bounding_box(*bounds)], [display_annotation])
    image_signal.mentions.append(display)

    return image_signal


def _create_text_signal(scenario: Scenario, utterance_data: Series):
    timestamp = utterance_data['time'] if 'time' in utterance_data else scenario.start
    utterance = utterance_data['utterance']
    signal = TextSignal.for_scenario(scenario.id, timestamp, timestamp, utterance_data['file'], utterance, [])

    offsets, tokens = zip(*[(Index(signal.id, start, end), Token.for_string(utterance[start:end]))
                            for start, end in TreebankWordTokenizer().span_tokenize(utterance)])
    annotations = [Annotation(AnnotationType.TOKEN.name.lower(), token, ANNOTATION_TOOL_ID, int(time.time()))
                   for token in tokens]
    signal.mentions.extend([Mention(str(uuid.uuid4()), [offset], [annotation])
                            for offset, annotation in zip(offsets, annotations)])

    return signal


class Backend:
    def __init__(self, data_path):
        self._storage = ScenarioStorage(data_path)

    def list_scenarios(self) -> Iterable[str]:
        return self._storage.list_scenarios()

    def load_scenario(self, scenario_id: str) -> Scenario:
        scenario = self._storage.load_scenario(scenario_id)
        if not scenario:
            scenario = self._create_scenario(scenario_id)
            self._storage.save_scenario(scenario)

        return scenario

    def _create_scenario(self, scenario_id: str) -> Scenario:
        start, end = self._storage.guess_scenario_range(scenario_id, _DEFAULT_SIGNALS.keys())

        return Scenario.new_instance(scenario_id, start, end,
                                     ScenarioContext("robot_agent", _SPEAKER, [], []),
                                     _DEFAULT_SIGNALS)

    def load_modality(self, scenario_id: str, modality: Modality) -> Iterable[Signal[Any, Any]]:
        signals = self._storage.load_modality(scenario_id, modality)
        if signals is None:
            signals = self._create_modality_metadata(scenario_id, modality)
            self._storage.save_signals(scenario_id, modality, signals)

        return signals

    def load_signal(self, scenario_id: str, modality: Modality, signal_id: str) -> Signal[Any, Any]:
        return self._storage.load_signal(scenario_id, modality, signal_id)

    def _create_modality_metadata(self, scenario_id, modality: Modality) -> Iterable[Signal[Any, Any]]:
        scenario = self.load_scenario(scenario_id)
        if modality.name.lower() == "image":
            image_meta = self._storage.load_images(self._storage.load_scenario(scenario_id))
            return [create_image_signal(scenario, meta) for _, meta in image_meta.iterrows()]
        elif modality.name.lower() == "text":
            texts = self._storage.load_text(scenario_id)
            return [_create_text_signal(scenario, utt) for _, utt in texts.iterrows()]
        else:
            raise ValueError("Unsupported modality " + modality.name)

    def save_signal(self, scenario_id: str, signal: Signal[Any, Any]) -> None:
        self._storage.save_signal(scenario_id, signal)

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

    def load_annotation_types(self) -> Iterable[Dict]:
        return self._storage.brain.get_annotation_types()

    def load_relation_types(self) -> Iterable[Dict]:
        return self._storage.brain.get_relation_types()

    def load_instances_of_type(self, class_type: str) -> Iterable[Dict]:
        return self._storage.brain.get_instances_of_type(class_type)


if __name__ == '__main__':
    backend = Backend("/Users/tkb/automatic/workspaces/robo/annotation/GMRCAnnotation/example_data")
    marshal(backend.load_modality("scenario_1", Modality.IMAGE))