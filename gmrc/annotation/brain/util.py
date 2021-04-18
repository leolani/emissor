from pathlib import Path

from rdflib import Graph, ConjunctiveGraph

from typing import Dict, Iterable

queries_path = Path(__file__).parent.resolve() / 'queries'
ontologies_path = Path(__file__).parent.resolve() / 'ontologies'
ememory_path = Path(__file__).parent.resolve() / 'episodic_memory'


def read_query(query_filename: str) -> str:
    file_path = queries_path / f"{query_filename}.rq"
    with open(file_path) as fr:
        query = fr.read()
    return query


def read_ontology() -> Graph:
    ontology_graph = Graph()
    for ontology_path in ontologies_path.glob('*.ttl'):
        ontology_graph.parse(location=str(ontology_path), format="turtle")

    return ontology_graph


def read_memories() -> ConjunctiveGraph:
    ememory_graph = ConjunctiveGraph()
    for episode_path in ememory_path.glob('*.trig'):
        ememory_graph.parse(location=str(episode_path), format="trig")

    return ememory_graph


def query_graph(graph: Graph, query: str) -> Iterable[Dict]:
    results = graph.query(query, DEBUG=True)
    if results:
        keys = results.vars
        results = [{str(field): row.get(str(field)) for field in keys} for row in results]

    return results


def get_annotation_types() -> Iterable[Dict]:
    ontology = read_ontology()
    query = read_query('classes_in_brain')
    annotation_types = query_graph(ontology, query)
    return annotation_types


def get_relation_types() -> Iterable[Dict]:
    ontology = read_ontology()
    query = read_query('relations_in_brain')
    relation_types = query_graph(ontology, query)
    return relation_types


def get_instances_of_type(instance_type: str) -> Iterable[Dict]:
    ememory = read_memories()
    query = read_query('instance_of_type') % instance_type
    annotation_instances = query_graph(ememory, query)
    return annotation_instances
