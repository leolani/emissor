from importlib.resources import path
from pathlib import Path
from typing import Dict, Iterable

from rdflib import Graph, ConjunctiveGraph


class Brain:

    def __init__(self, ememory_path):
        self.ememory_path = Path(ememory_path).resolve()

        with path('gmrc.annotation.brain', 'queries') as p:
            self.queries_path = p

        with path('gmrc.annotation.brain', 'world_model') as p:
            self.ontologies_path = p

        self.ontology = self._load_ontology()
        self.ememory = self._load_memories()

    def _read_query(self, query_filename: str) -> str:
        file_path = self.queries_path / f"{query_filename}.rq"
        with open(file_path) as fr:
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
        for ontology_path in self.ontologies_path.glob('*.ttl'):
            ontology_graph.parse(location=str(ontology_path), format="turtle")

        return ontology_graph

    def _load_memories(self, ) -> ConjunctiveGraph:
        ememory_graph = ConjunctiveGraph()
        for episode_path in self.ememory_path.glob('*.trig'):
            ememory_graph.parse(location=str(episode_path), format="trig")

        return ememory_graph

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
