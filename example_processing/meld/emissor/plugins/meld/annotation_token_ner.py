import logging
import spacy
import time
import uuid
from tqdm import tqdm
from typing import Tuple, Mapping, Iterable

from emissor.persistence.persistence import ScenarioController
from emissor.processing.api import SignalProcessor
from emissor.representation.annotation import AnnotationType, Token, NER
from emissor.representation.container import Index
from emissor.representation.scenario import Modality, Mention, Annotation, Signal

logger = logging.getLogger(__name__)


class MeldNERProcessor(SignalProcessor):
    def __enter__(self):
        self._nlp = spacy.load('en_core_web_sm')

    @property
    def parallel(self) -> bool:
        return True

    @property
    def modalities(self) -> Tuple[Modality]:
        return (Modality.TEXT,)

    def process_signals(self, scenario: ScenarioController, signals: Mapping[Modality, Iterable[Signal]]):
        logger.info("Add tokenization and NER annotations to %s", scenario.id)
        text_signals = tuple(signals[Modality.TEXT])
        with tqdm(text_signals) as progress:
            cnt = 0
            for signal in progress:
                # TODO: check if annotations already exist
                cnt += self.add_ner_annotations(signal)
                progress.set_postfix({'NER count': cnt})

    def process_signal(self, scenario: ScenarioController, signal: Signal):
        if not signal.modality == Modality.TEXT:
            return

        self.add_ner_annotations(signal)

    def add_ner_annotations(self, signal: Signal):
        utterance = ''.join(signal.seq)

        doc = self._nlp(utterance)

        offsets, tokens = zip(*[(Index(signal.id, token.idx, token.idx+len(token)), Token.for_string(token.text))
                                for token in doc])

        ents = [NER.for_string(ent.label_) for ent in doc.ents]
        entity_text = [ent.text for ent in doc.ents]
        segments = [token.ruler for token in tokens if token.value in entity_text]

        annotations = [Annotation(AnnotationType.TOKEN.name.lower(), token, self.name, int(time.time()))
                       for token in tokens]
        ner_annotations = [Annotation(AnnotationType.NER.name.lower(), ent, self.name, int(time.time()))
                           for ent in ents]

        signal.mentions.extend([Mention(str(uuid.uuid4()), [offset], [annotation])
                                for offset, annotation in zip(offsets, annotations)])
        signal.mentions.extend([Mention(str(uuid.uuid4()), [segment], [annotation])
                                for segment, annotation in zip(segments, ner_annotations)])

        return len(ner_annotations)
