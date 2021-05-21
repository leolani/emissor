import os

from importlib.resources import path, open_text, files
from pathlib import Path
from typing import Dict, Iterable

from rdflib import Graph, ConjunctiveGraph, URIRef, Namespace

import emissor


class EmissorBrain:
    def __init__(self, ememory_path):

        # TODO: Similar to robot platform, a brain needs an RDF Builder (taken from cltl-knowledge representation)
        # Porting this should give us access to automatic creation of entities, triples, namespaces and named graphs
        # self._rdf_builder = RdfBuilder()

        # Create graphs: world model, memory and current experiences
        self.ememory_path = Path(ememory_path).resolve()
        self.interpretations_path = self.ememory_path.parent

        self.ontology = self._load_ontology()
        self.ememory = self._load_memories()
        self.interpretations_graph = self._create_episode_graph()

    def _read_query(self, query_filename: str) -> str:
        with open_text(emissor.annotation.brain, f"queries/{query_filename}.rq") as fr:
            query = fr.read()
        return query

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

    def denote_things(self, mention, annotation):
        # TODO we assume the value of the annotation to be a valid URI,
        #  but we still have to check this as there is no data to test

        # Create and bind namespaces
        # TODO this will be much easier once we have the full brain functionality
        ltalk_ns = Namespace('http://cltl.nl/leolani/talk/')
        self.interpretations_graph.bind('leolaniTalk', ltalk_ns)
        gaf_ns = Namespace('http://groundedannotationframework.org/gaf#')
        self.interpretations_graph.bind('gaf', gaf_ns)

        # Create triple
        mention_uri = ltalk_ns[mention.id]
        instance_uri = URIRef(annotation.value.value)
        self.interpretations_graph.add((instance_uri, gaf_ns['denotedBy'], mention_uri))

        # Save to file but return the string representation
        os.makedirs(f'{self.interpretations_path}', exist_ok=True)
        with open(f'{self.interpretations_path}/annotation_{annotation.value.id}.trig', 'wb') as f:
            self.interpretations_graph.serialize(f, format="trig")

        data = self.interpretations_graph.serialize(format="trig")

        # TODO we return the serialized graph with the new triples. TBD if we want to
        #  a) create a new graph per annotation, VS accumulate on the same graph
        #  b) return the triples or save them
        return data.decode("utf-8")
