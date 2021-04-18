from flask import Flask, request
from flask_cors import CORS

from gmrc.annotation.backend import Backend
from gmrc.annotation.brain.util import get_annotation_types, get_relation_types, get_instances_of_type
from gmrc.representation.scenario import Modality
from gmrc.representation.util import unmarshal, marshal


def create_app(data_path):
    app = Flask(__name__, static_url_path='/data', static_folder=data_path)
    CORS(app)

    backend = Backend(data_path)

    @app.route('/api/scenario')
    def list_scenario():
        return marshal(backend.list_scenarios())

    @app.route('/api/scenario/<name>')
    def load_scenario(name):
        return marshal(backend.load_scenario(name))

    @app.route('/api/scenario/<name>/<modality>')
    def load_signals(name, modality):
        return marshal(backend.load_modality(name, Modality[modality.upper()]))

    @app.route('/api/scenario/<scenario_id>/<modality>/<signal>', methods=['POST'])
    def save_signal(scenario_id, modality, signal):
        signal_json = request.get_data(as_text=True)
        backend.save_signal(scenario_id, unmarshal(signal_json))

        return ""

    @app.route('/api/scenario/<scenario_id>/<modality>/<signal_id>/mention', methods=['PUT'])
    def create_mention(scenario_id: str, modality: str, signal_id: str):
        return marshal(backend.create_mention(scenario_id, Modality[modality.upper()], signal_id))

    @app.route('/api/scenario/<scenario_id>/<modality>/<signal_id>/<mention_id>/annotation', methods=['PUT'])
    def create_annotation(scenario_id: str, modality: str, signal_id: str, mention_id: str):
        type_ = request.args.get("type")
        return marshal(backend.create_annotation(type_))

    @app.route('/api/scenario/<scenario_id>/<modality>/<signal_id>/<mention_id>/segment', methods=['PUT'])
    def create_segment(scenario_id: str, modality: str, signal_id: str, mention_id: str):
        type_ = request.args.get("type")
        container_id = request.args.get("container")

        return marshal(
            backend.create_segment(scenario_id, Modality[modality.upper()], signal_id, mention_id, type_, container_id))

    @app.route('/test')
    def test():
        from pprint import pprint
        pprint(app.url_map)

        return str(app.url_map)

    @app.route('/api/annotation/class_types')
    def load_annotation_types():
        return marshal(get_annotation_types())

    @app.route('/api/annotation/relation_types')
    def load_relation_types():
        return marshal(get_relation_types())

    @app.route('/api/annotation/<class_type>/instances')
    def load_annotation_instances(class_type):
        return marshal(get_instances_of_type(class_type))

    return app
