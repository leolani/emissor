import time
import uuid

import spacy

from emissor.annotation.persistence import ScenarioStorage, ANNOTATION_TOOL_ID, SPACY_ID
from emissor.representation.annotation import AnnotationType, Token, NER
from emissor.representation.container import Index, AtomicRuler
from emissor.representation.scenario import Modality, TextSignal, Mention, Annotation

nlp = spacy.load('en_core_web_sm')


def _add_ner_annotation(signal: TextSignal):
    # TODO: check if annotations already exist

    utterance = ''.join(signal.seq)

    doc = nlp(utterance)

    offsets, tokens = zip(*[(Index(signal.id, token.idx, token.idx+len(token)), Token.for_string(token.text))
                            for token in doc])

    ents = [NER.for_string(ent.label_) for ent in doc.ents]
    entity_text = [ent.text for ent in doc.ents]
    segments = [AtomicRuler(token.id) for token in tokens if token.value in entity_text]

    annotations = [Annotation(AnnotationType.TOKEN.name.lower(), token, ANNOTATION_TOOL_ID, int(time.time()))
                   for token in tokens]
    ner_annotations = [Annotation(AnnotationType.NER.name, ent, SPACY_ID, int(time.time())) for ent in ents]

    signal.mentions.extend([Mention(str(uuid.uuid4()), [offset], [annotation])
                            for offset, annotation in zip(offsets, annotations)])
    signal.mentions.extend([Mention(str(uuid.uuid4()), [segment], [annotation])
                            for segment, annotation in zip(segments, ner_annotations)])

    return signal

def annotate_scenario(data_path):
    storage = ScenarioStorage(data_path)
    scenario_ids = storage.list_scenarios()

    for scenario_id in scenario_ids:
        print(scenario_id)
        signals = storage.load_modality(scenario_id, Modality.TEXT)
        if signals is None:
            raise ValueError("Signals not found")
            # if we want to skip we could do continue, but print warning message
        for signal in signals:
            # check if annotations exist
            _add_ner_annotation(signal)
        storage.save_signals(scenario_id, Modality.TEXT, signals)

# def check_annotation_existence(signal):


if __name__ == '__main__':
    annotate_scenario('/Users/jaap/Documents/GitHub/GMRCAnnotation/test_data')