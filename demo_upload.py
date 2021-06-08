import time
from glob import glob

from rdflib import ConjunctiveGraph
import requests


def upload(filename):
    graph = ConjunctiveGraph()
    graph.parse(filename, format="trig")
    data = graph.serialize(format="trig")
    print(requests.post("http://localhost:7200/repositories/demo/statements", data=data,
                  headers={'Content-Type': 'application/x-trig'}), filename)


def bootstrap():
    graph = ConjunctiveGraph()
    graph.parse("emissor/annotation/brain/world_model/ceo.ttl", format="turtle")
    graph.parse("emissor/annotation/brain/world_model/integration.ttl", format="turtle")
    data = graph.serialize(format="trig")
    print(requests.post("http://localhost:7200/repositories/demo/statements", data=data,
                  headers={'Content-Type': 'application/x-trig'}), "bootstrap")


if __name__ == '__main__':
    bootstrap()
    sec = input('Let us wait for user input. Let me know how many seconds to sleep now.\n')
    for file in glob("example_data/demo/scenarios/**/rdf/*.trig"):
        upload(file)
        sec = input('Let us wait for user input. Let me know how many seconds to sleep now.\n')
