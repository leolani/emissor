from typing import Union

import json
from flask import Flask, jsonify, request
from flask_cors import CORS

from grmc.backend import Backend
from grmc.representation.scenario import Signal
from grmc.representation.util import serializer

app = Flask(__name__)
CORS(app)


backend = Backend()


@app.route('/api/scenario')
def list_scenario():
    return jsonify(backend.list_scenarios())


@app.route('/api/scenario/<name>')
def load_scenario(name):
    return json.dumps(backend.load_scenario(name), default=serializer)


@app.route('/api/scenario/<name>/<modality>')
def load_signals(name, modality):
    return json.dumps(backend.load_modality(name, modality), default=serializer)


@app.route('/api/scenario/<scenario_id>/<modality>/<signal>', methods=['POST'])
def save_signal(scenario_id, modality, signal):
    signal_json = request.get_json()
    backend.save_signal(scenario_id, unmarshal(signal_json, Signal(None, None, None)))

    return {}, 200


def unmarshal(json: Union[dict, list, int, float, bool, str, None], obj: object) -> object:
    if isinstance(json, list):
        return [unmarshal(entry, obj) for entry in json]
    if isinstance(json, (int, float, bool, str)) or None:
        return json
    if isinstance(json, dict):
        for key, value in json:
            try:
                setattr(object, key, unmarshal(value, obj))
            except AttributeError:
                pass
