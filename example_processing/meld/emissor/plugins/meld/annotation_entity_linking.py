import logging
import time
from rdflib import Namespace, URIRef
from typing import Iterable

from emissor.annotation.brain.util import EmissorBrain
from emissor.persistence import ScenarioStorage
from emissor.processing.api import SignalProcessor
from emissor.representation.annotation import AnnotationType, Entity
from emissor.representation.scenario import Modality, TextSignal, Annotation, ImageSignal, Signal, Scenario

logger = logging.getLogger(__name__)


PERSON_NAMESPACE = Namespace("http://cltl.nl/leolani/n2mu/person#")


class MeldEntityLinkingProcessor(SignalProcessor):
    def process(self, scenario: Scenario, modality: Modality, signals: Iterable[Signal], storage: ScenarioStorage):
        if modality is Modality.IMAGE:
            self.link_image_signals(signals, storage.brain)
        elif modality is Modality.TEXT:
            self.link_text_signals(signals, storage.brain)
        else:
            return

        storage.save_signals(scenario.id, Modality.IMAGE, signals)

    def link_image_signals(self, signals: Iterable[ImageSignal], brain: EmissorBrain):
        if signals is None:
            raise ValueError("Signals not found")
            # if we want to skip we could do continue, but print warning message
        for signal in signals:
            # check if annotations exist
            self.add_face_entity_links(signal, brain)

    def link_text_signals(self, signals: Iterable[TextSignal], brain: EmissorBrain):
        if signals is None:
            raise ValueError("Signals not found")
            # if we want to skip we could do continue, but print warning message
        for signal in signals:
            # check if annotations exist
            self.add_ner_entity_links(signal, brain)

    def add_ner_entity_links(self, signal: TextSignal, brain: EmissorBrain):
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

            uri = self.resolve_name(token.value if token else None, brain)
            link_annotation = Annotation(AnnotationType.LINK.name, Entity(uri), self.name, int(time.time()))
            mention.annotations.append(link_annotation)

            brain.denote_things(mention, link_annotation)

    def add_face_entity_links(self, signal: ImageSignal, brain: EmissorBrain):
        # TODO: check if annotations already exist
        ner_mentions = [(mention, annotation)
                        for mention in signal.mentions
                        for annotation in mention.annotations
                        if annotation.type.lower() == AnnotationType.PERSON.name.lower()]

        for mention, annotation in ner_mentions:
            name = annotation.value.name
            uri = self.resolve_name(name, brain)
            link_annotation = Annotation(AnnotationType.LINK.name, Entity(uri), self.name, int(time.time()))
            mention.annotations.append(link_annotation)

            brain.denote_things(mention, link_annotation)

    def resolve_name(self, name: str, brain: EmissorBrain) -> URIRef:
        if not name:
            return brain.add_person("UNKNOWN")

        known = next(iter(brain.find_persons(name)), None)
        if known:
            return known

        return brain.add_person(name)