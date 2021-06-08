import logging
import spacy
import time

from emissor.annotation.brain.util import EmissorBrain
from emissor.annotation.persistence import ScenarioStorage
from emissor.representation.annotation import AnnotationType, EntityLink
from emissor.representation.scenario import Modality, TextSignal, Annotation, ImageSignal

logger = logging.getLogger(__name__)

nlp = spacy.load('en_core_web_sm')


SPACY_ID = "SpaCY"


def _add_ner_entity_links(signal: TextSignal, brain: EmissorBrain):
    # TODO: check if annotations already exist
    ner_mentions = [(mention, annotation)
                    for mention in signal.mentions
                    for annotation in mention.annotations
                    if (annotation.type.lower() == AnnotationType.NER.name.lower()
                        and annotation.value.value.lower() == "person")]

    for mention, annotation in ner_mentions:
        token = None
        try:
            container = mention.segment[0].container_id
            annotation = [annotation
                          for mention in signal.mentions
                          for annotation in mention.annotations
                          if hasattr(annotation.value, "id") and annotation.value.id == container]
            assert len(mention.segment) == 1 and len(annotation) == 1

            token = annotation[0].value
        except:
            pass

        if token:
            uri = next(iter(brain.find_persons(token.value)), None)
            id = str(uri).split("/")[-1] if uri else brain.add_person(token.value)
        else:
            id = brain.add_person("UNKNOWN")

        link_annotation = Annotation(AnnotationType.LINK.name, EntityLink(id), "linkin_tool", int(time.time()))
        mention.annotations.append(link_annotation)

        brain.denote_things(mention, link_annotation)

    return signal


def _add_face_entity_links(signal: ImageSignal, brain: EmissorBrain):
    # TODO: check if annotations already exist
    ner_mentions = [(mention, annotation)
                    for mention in signal.mentions
                    for annotation in mention.annotations
                    if annotation.type.lower() == AnnotationType.PERSON.name.lower()]

    for mention, annotation in ner_mentions:
        name = annotation.value.name
        if name:
            uri = next(iter(brain.find_persons(name)), None)
            id = str(uri).split("/")[-1] if uri else brain.add_person(name)
        else:
            id = brain.add_person("UNKNOWN")

        link_annotation = Annotation(AnnotationType.LINK.name, EntityLink(id), "linkin_tool", int(time.time()))
        mention.annotations.append(link_annotation)

        brain.denote_things(mention, link_annotation)

    return signal

def annotate_scenarios(storage: ScenarioStorage):
    scenario_ids = storage.list_scenarios()

    for scenario_id in scenario_ids:
        logger.info("Add tokenization and NER annotations to %s", scenario_id)

        # Load episodic memory
        storage.load_scenario(scenario_id)
        link_image_signals(scenario_id, storage)
        link_text_signals(scenario_id, storage)


def link_image_signals(scenario_id, storage):
    signals = storage.load_modality(scenario_id, Modality.IMAGE)
    if signals is None:
        raise ValueError("Signals not found")
        # if we want to skip we could do continue, but print warning message
    for signal in signals:
        # check if annotations exist
        _add_face_entity_links(signal, storage.brain)
    storage.save_signals(scenario_id, Modality.IMAGE, signals)


def link_text_signals(scenario_id, storage):
    signals = storage.load_modality(scenario_id, Modality.TEXT)
    if signals is None:
        raise ValueError("Signals not found")
        # if we want to skip we could do continue, but print warning message
    for signal in signals:
        # check if annotations exist
        _add_ner_entity_links(signal, storage.brain)
    storage.save_signals(scenario_id, Modality.TEXT, signals)
