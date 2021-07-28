
import logging
import spacy
import time
import uuid
from datetime import datetime
from emissor.persistence import ScenarioStorage
from emissor.representation.annotation import AnnotationType, Token, NER
from emissor.representation.container import Index
from emissor.representation.scenario import Modality, TextSignal, Mention, Annotation, Scenario

def add_ner_annotation(signal: TextSignal):
    processor_name = "spaCy"
    utterance = ''.join(signal.seq)

    doc = nlp(utterance)

    offsets, tokens = zip(*[(Index(signal.id, token.idx, token.idx+len(token)), Token.for_string(token.text))
                            for token in doc])

    ents = [NER.for_string(ent.label_) for ent in doc.ents]
    entity_text = [ent.text for ent in doc.ents]
    segments = [token.ruler for token in tokens if token.value in entity_text]

    annotations = [Annotation(AnnotationType.TOKEN.name.lower(), token,processor_name, int(time.time()))
                   for token in tokens]
    ner_annotations = [Annotation(AnnotationType.NER.name.lower(), ent, processor_name, int(time.time()))
                       for ent in ents]

    signal.mentions.extend([Mention(str(uuid.uuid4()), [offset], [annotation])
                            for offset, annotation in zip(offsets, annotations)])
    signal.mentions.extend([Mention(str(uuid.uuid4()), [segment], [annotation])
                            for segment, annotation in zip(segments, ner_annotations)])

    return entity_text

def create_text_signal(scenario: Scenario, utterance: str, start: int, end: int):
    signal = TextSignal.for_scenario(scenario.id, start, end, "./text.json", utterance, [])
    return signal


if __name__ == '__main__':
    agent = "Leolani"
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    logger = logging.getLogger(__name__)
    nlp = spacy.load('en_core_web_sm')

    scenarioid = "myscenario"
    scenario_path = "../../../data"
    scenarioStorage = ScenarioStorage(scenario_path)

    signals = {
        Modality.IMAGE.name.lower(): "./image.json",
        Modality.TEXT.name.lower(): "./text.json"
    }
    scenario = Scenario.new_instance(scenarioid, now, now, agent, signals)
    scenarioStorage.add_scenario(scenarioid, scenario)

    scenarioStorage.save_scenario(scenario)
    scenarioStorage.init_modality(Modality.TEXT)

    utterance = input(agent+":"+"Hi there. Who are you?"+'\n\n')
    print("you:"+utterance)
    while not (utterance=='stop'):
        textSignal = create_text_signal(scenario, utterance, 1, 2)
        entityText = add_ner_annotation(textSignal)

        scenarioStorage.add_signal(Modality.TEXT, textSignal)

        if not entityText:
            utterance = input(agent+":"+"Any gossip" + '\n')
        else:
            utterance = input(agent+":"+"So you what do you want to talk about" + entityText[0] + '\n')
        print("you:"+utterance)

    scenarioStorage.serialise_signals(scenarioid, Modality.TEXT)