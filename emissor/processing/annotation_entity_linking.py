import time
import uuid

import spacy

from emissor.annotation.brain.util import EmissorBrain
from emissor.annotation.persistence import ScenarioStorage
from emissor.representation.annotation import AnnotationType, Token, NER, EntityLink
from emissor.representation.container import Index, AtomicRuler
from emissor.representation.scenario import Modality, TextSignal, Mention, Annotation

nlp = spacy.load('en_core_web_sm')


SPACY_ID = "SpaCY"


def _add_entity_links(signal: TextSignal):
    # TODO: check if annotations already exist
    ner_mentions = [(mention, annotation)
                    for mention in signal.mentions
                    for annotation in mention.annotations
                    if annotation.type.lower() == AnnotationType.NER.name.lower()]

    for mention, annotation in ner_mentions:
        mention.annotations.append(EntityLink(uuid.uuid4()))

    return signal


def annotate_scenarios(data_path):
    storage = ScenarioStorage(data_path)
    scenario_ids = storage.list_scenarios()

    for scenario_id in scenario_ids:
        # Load episodic memory
        storage.load_scenario(scenario_id)
        signals = storage.load_modality(scenario_id, Modality.TEXT)
        if signals is None:
            raise ValueError("Signals not found")
            # if we want to skip we could do continue, but print warning message
        for signal in signals:
            # check if annotations exist
            _add_entity_links(signal, storage.brain)
        storage.save_signals(scenario_id, Modality.TEXT, signals)


if __name__ == '__main__':
    annotate_scenarios('/Users/jaap/Documents/GitHub/GMRCAnnotation/test_data')