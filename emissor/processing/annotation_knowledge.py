import logging
import uuid
from datetime import date

import numpy as np
import spacy
import time

from cltl.brain import LongTermMemory
from cltl.brain.infrastructure.rdf_builder import RdfBuilder
from cltl.brain.infrastructure.api import Perspective, Entity, Predicate
from cltl.brain.api import Context, Face, Object, Chat, Utterance, UtteranceHypothesis
from cltl.combot.backend.api.discrete import UtteranceType, Emotion
from cltl.combot.infra.util import Bounds
from emissor.annotation.persistence import ScenarioStorage
from emissor.representation.annotation import AnnotationType, EntityLink
from emissor.representation.scenario import Modality, TextSignal, Annotation, Scenario

logger = logging.getLogger(__name__)

nlp = spacy.load('en_core_web_sm')


TEST_IMG = np.zeros((128,))
TEST_BOUNDS = Bounds(0.0, 0.0, 0.5, 1.0)

name = 'Leolani'
places = ['Forest', 'Playground', 'Monastery', 'House', 'University', 'Hotel', 'Office']
friends = ['Piek', 'Lenka', 'Bram', 'Suzana', 'Selene', 'Lea', 'Thomas', 'Jaap', 'Tae']

signal = False
binary_values = [True]


SPACY_ID = "SpaCY"


def _add_entity_links(signal: TextSignal, chat: Chat, brain: LongTermMemory):
    # TODO: check if annotations already exist
    ner_mentions = [(mention, annotation)
                    for mention in signal.mentions
                    for annotation in mention.annotations
                    if annotation.type.lower() == AnnotationType.NER.name.lower()]

    for mention, annotation in ner_mentions:
        link_annotation = Annotation(AnnotationType.LINK.name, EntityLink(uuid.uuid4()), "linking_tool", int(time.time()))
        mention.annotations.append(link_annotation)
        utterance = _create_utterance(chat, "", 1)
        entity = "Carl"
        complement = {"label": entity, "type": str(annotation.value)}

        _add_triple(utterance, complement, {"type": "sees"}, {"label": "pills", "type": "object"})

        brain.experience(utterance)

    return signal


def annotate_scenarios(storage, brain=None):
    scenario_ids = storage.list_scenarios()
    brain = brain if brain else LongTermMemory()

    for scenario_id in scenario_ids:
        logger.info("Add tokenization and NER annotations to %s", scenario_id)

        # Load episodic memory
        scenario = storage.load_scenario(scenario_id)
        chat = create_chat(scenario)

        signals = storage.load_modality(scenario_id, Modality.TEXT)
        if signals is None:
            raise ValueError("Signals not found")
            # if we want to skip we could do continue, but print warning message
        for signal in signals:
            # check if annotations exist
            _add_entity_links(signal, chat, brain)
        storage.save_signals(scenario_id, Modality.TEXT, signals)


def create_chat(scenario: Scenario) -> Chat:
    context = _create_context(scenario)
    context.set_datetime(scenario.start)

    chat = Chat(scenario.context.speaker.name, context)
    chat.id = scenario.id

    return chat


def _create_context(scenario: Scenario) -> Context:
    context = Context(name, friends)

    objects = [Object(obj.label, 0.79, TEST_BOUNDS, TEST_IMG) for obj in scenario.context.objects]
    context.add_objects(objects)

    faces = [Face(pers.name, .90, .90, TEST_BOUNDS, TEST_IMG) for pers in scenario.context.persons]
    context.add_people(faces)

    return context


def _create_utterance(chat, utterance_text, turn):
    hyp = UtteranceHypothesis(utterance_text, 0.99)

    utt = Utterance(chat, [hyp], False, turn)
    utt._type = UtteranceType.STATEMENT
    utt.turn = turn

    return utt


def _add_triple(utt, subject, predicate, object):
    builder = RdfBuilder()
    utt.triple = builder.fill_triple(subject, predicate, object)

    sentiment = 0.0
    emotion = Emotion.NEUTRAL
    certainty = 1
    polarity = 1

    utt.perspective = Perspective(certainty, polarity, sentiment, emotion=emotion)


if __name__ == '__main__':
    annotate_scenarios('/Users/jaap/Documents/GitHub/GMRCAnnotation/test_data')