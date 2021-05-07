import dataclasses
import json
import os
from dataclasses import dataclass
from pprint import pprint

import rdflib
from rdflib import Graph, plugin, RDF, OWL
from rdflib.namespace import split_uri
from rdflib.serializer import Serializer

from emissor.representation.util import marshal, unmarshal


def test():

    g = Graph().parse(location="grasp_original.rdf")

    @dataclass
    class Test:
        name: str

    test = dataclasses.replace(Test("test"))
    test.__setattr__("@context", { "test": "testtest"})
    print(marshal(test))

    print(unmarshal(json.dumps(test, default=vars), Test))
    # print(g.serialize(format='ttl', indent=4, context=context).decode('utf-8'))
    # onto_ld = g.serialize(format='json-ld', indent=4).decode('utf-8')
    # print(onto_ld)
    # g = Graph().parse(data=onto_ld, format='json-ld')

    print("NS", [n for n in g.namespaces()])
    print([split_uri(t) for t in g.subjects(RDF.type, OWL.Class) if isinstance(t, rdflib.URIRef)])
    print([split_uri(t) for t in g.subjects(RDF.type, OWL.ObjectProperty) if isinstance(t, rdflib.URIRef)])
    print([split_uri(t) for t in g.subjects(RDF.type) if isinstance(t, rdflib.URIRef)])
    print([g.namespace_manager.qname(t) for t in g.subjects(RDF.type) if isinstance(t, rdflib.URIRef)])
    # print([t for t in g])


    # Ontologies -> select concept & relations names, precedence defined by ontology order



    print("\n\n\n")
    print(g.serialize(format='ttl', indent=4).decode('utf-8'))
    # {
    #     "@id": "http://example.org/about",
    #     "http://purl.org/dc/terms/title": [
    #         {
    #             "@language": "en",
    #             "@value": "Someone's Homepage"
    #         }
    #     ]
    # }


def create_context(*ontologies):
    return merge_safely(*[create_ontology_context(ontology) for ontology in ontologies])


def create_ontology_context(ontology):
    context = dict()

    graph = load_graph(ontology)

    namespace_manager = graph.namespace_manager

    ontology_namespace = dict([extract_alias(t, namespace_manager) for t in graph.subjects(RDF.type, OWL.Ontology)])
    context = merge_safely(context, ontology_namespace)

    namespaces = dict(namespace_manager.namespaces())
    base = None
    try:
        base_uri = namespaces.pop('')
        base = next(k for k, v in ontology_namespace.items() if v == base_uri)
    except StopIteration:
        base, base_uri = extract_alias(base_uri, namespace_manager)
    except KeyError:
        # There is no @base URI defined
        pass

    context = merge_safely(context, namespaces)

    type_qnames = (namespace_manager.qname(t[0]) for t in graph.subject_objects(RDF.type)
             if isinstance(t[0], rdflib.URIRef) and not t[1] == OWL.Ontology)
    type_aliases = {("_".join(t.split(":")), t) if ":" in t else (t, base + ":" + t) for t in type_qnames}
    types = dict(type_aliases)

    assert len(types) == len(type_aliases), str(sorted(type_aliases))

    context = merge_safely(context, types)

    return {k: str(v) for k, v in context.items()}


def extract_alias(uri, namespace_manager):
    try:
        return split_uri(uri)[1], uri + "#"
    except ValueError:
        uri_str = str(uri)
        if not uri_str.endswith(('/', "#")):
            raise ValueError("Cannot extract alias for " + uri_str)

        return split_uri(uri_str[:-1])[1], uri


def load_graph(ontology):
    file_format = os.path.splitext(ontology)[1][1:]
    if file_format:
        try:
            return Graph().parse(location=ontology, format=file_format)
        except rdflib.plugin.PluginException:
            # Try if the format can be resolved automatically
            pass

    return Graph().parse(location=ontology)


def merge_safely(*dicts):
    merged = dict()
    for current in dicts:
        unique_items = set().union(merged.items(), current.items())
        unique_keys = current.keys() | merged.keys()
        if len(unique_items) != len(unique_keys):
            conflicts = {key: (merged[key], current[key])
                         for key in current.keys() & merged.keys()
                         if merged[key] != current[key]}
            raise ValueError("Name conflicts: " + str(conflicts))

        merged = merged | current

    return merged


pprint(create_context("integration.ttl"))