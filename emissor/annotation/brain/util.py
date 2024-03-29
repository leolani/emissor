import uuid

import os
from importlib_resources import files
from pathlib import Path
from rdflib import Graph, ConjunctiveGraph, URIRef, Namespace, RDF, Literal
from rdflib.namespace import split_uri
from typing import Dict, Iterable

import emissor
from emissor.representation.annotation import AnnotationType
from emissor.representation.scenario import Annotation, Mention

ENTITY_ANNOTATIONS = {type.name.upper() for type in [AnnotationType.LINK, AnnotationType.PERSON, AnnotationType.FRIEND, AnnotationType.OBJECT]}


class EmissorBrain:
    def __init__(self, ememory_path, scenario_id):

        # TODO: Similar to robot platform, a brain needs an RDF Builder (taken from cltl-knowledge representation)
        # Porting this should give us access to automatic creation of entities, triples, namespaces and named graphs
        # self._rdf_builder = RdfBuilder()

        # Create graphs: world model, memory and current experiences
        self.ememory_path = Path(ememory_path).resolve()
        self.scenario_id = scenario_id
        self.interpretations_path = self.ememory_path.parent

        self.ontology = self._load_ontology()
        self.ememory = self._load_memories()
        self.interpretations_graph = self._create_episode_graph()

    def _read_query(self, query_filename: str) -> str:
        return files('emissor.annotation.brain').joinpath(f"queries/{query_filename}.rq").read_text()

    def _query_graph(self, graph: Graph, query: str) -> Iterable[Dict]:
        results = graph.query(query)
        if results:
            keys = results.vars
            results = [{str(field): row.get(str(field)) for field in keys} for row in results]

        return results

    def _load_ontology(self) -> Graph:
        ontology_graph = Graph()
        for ontology_path in files(emissor.annotation.brain).joinpath('world_model').glob('*.ttl'):
            ontology_graph.parse(location=str(ontology_path), format="turtle")

        return ontology_graph

    def _load_memories(self, ) -> ConjunctiveGraph:
        ememory_graph = ConjunctiveGraph()
        for episode_path in self.ememory_path.glob('*.trig'):
            ememory_graph.parse(location=str(episode_path), format="trig")

        return ememory_graph

    def _create_episode_graph(self) -> ConjunctiveGraph:
        episode_graph = ConjunctiveGraph()

        return episode_graph

    def get_annotation_types(self) -> Iterable[Dict]:
        query = self._read_query('classes_in_brain')
        annotation_types = self._query_graph(self.ontology, query)
        return annotation_types

    def get_relation_types(self) -> Iterable[Dict]:
        query = self._read_query('relations_in_brain')
        relation_types = self._query_graph(self.ontology, query)
        return relation_types

    def get_instances_of_type(self, instance_type: str) -> Iterable[Dict]:
        query = self._read_query('instance_of_type') % instance_type
        annotation_instances = self._query_graph(self.ememory, query)
        return annotation_instances

    def find_persons(self, label):
        return [p for p in self.interpretations_graph.subjects(URIRef("n2mu:name"), Literal(label))] + \
               [p for p in self.ememory.subjects(URIRef("n2mu:name"), Literal(label))]

    def add_person(self, label):
        friends_ns = Namespace('http://cltl.nl/leolani/friends/')
        self.interpretations_graph.bind('leolaniFriend', friends_ns)
        iri = friends_ns[str(uuid.uuid4())]
        self.interpretations_graph.add((iri, RDF.type, URIRef("n2mu:person")))
        self.interpretations_graph.add((iri, URIRef("n2mu:name"), Literal(label)))

        return iri

    def denote_things(self, mention: Mention, annotation: Annotation):
        if str(annotation.type).upper() not in ENTITY_ANNOTATIONS:
            raise ValueError(f"Cannot denote {annotation} of type {annotation.type}")

        # Create and bind namespaces
        # TODO this will be much easier once we have the full brain functionality
        ltalk_ns = Namespace('http://cltl.nl/leolani/talk/')
        self.interpretations_graph.bind('leolaniTalk', ltalk_ns)
        gaf_ns = Namespace('http://groundedannotationframework.org/gaf#')
        self.interpretations_graph.bind('gaf', gaf_ns)

        # Create triple
        mention_uri = ltalk_ns[mention.id]
        instance_uri = annotation.value.id
        self.interpretations_graph.add((instance_uri, gaf_ns['denotedBy'], mention_uri))

        # Save to file but return the string representation
        os.makedirs(f'{self.interpretations_path}', exist_ok=True)
        id = split_uri(instance_uri)[-1]
        with open(f'{self.interpretations_path}/annotation_{id}.trig', 'wb') as f:
            self.interpretations_graph.serialize(f, format="trig")

        data = self.interpretations_graph.serialize(format="trig")

        # TODO we return the serialized graph with the new triples. TBD if we want to
        #  a) create a new graph per annotation, VS accumulate on the same graph
        #  b) return the triples or save them
        return data.decode("utf-8")
