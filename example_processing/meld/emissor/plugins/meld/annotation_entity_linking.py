import logging
import os
import time
from rdflib import Namespace, URIRef
from typing import Tuple

from emissor.annotation.brain.util import EmissorBrain
from emissor.persistence.persistence import ScenarioController
from emissor.processing.api import SignalProcessor
from emissor.representation.annotation import AnnotationType, Entity
from emissor.representation.scenario import Modality, TextSignal, Annotation, ImageSignal, Signal

logger = logging.getLogger(__name__)


PERSON_NAMESPACE = Namespace("http://cltl.nl/leolani/n2mu/person#")


class MeldEntityLinkingProcessor(SignalProcessor):
    def __init__(self, base_path):
        self._base_path = base_path
        self._brain_cache = dict()

    @property
    def modalities(self) -> Tuple[Modality]:
        return (Modality.TEXT, Modality.IMAGE)

    def process_signal(self, scenario: ScenarioController, signal: Signal):
        ememory_path = os.path.join(self._base_path, scenario.id, 'rdf', 'episodic_memory')
        if ememory_path in self._brain_cache:
            brain = self._brain_cache[ememory_path]
        else:
            brain = EmissorBrain(ememory_path)
            self._brain_cache.clear()
            self._brain_cache[ememory_path] = brain

        if signal.modality == Modality.TEXT:
            self.add_ner_entity_links(signal, brain)
        elif signal.modality == Modality.IMAGE:
            self.add_face_entity_links(signal, brain)
        else:
            raise ValueError("Unsupported modality " + signal.modality.name)

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
