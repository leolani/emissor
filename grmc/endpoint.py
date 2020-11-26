from flask import Flask, request
from flask_cors import CORS

from grmc.backend import Backend
from grmc.representation.util import unmarshal, marshal

app = Flask(__name__)
CORS(app)


backend = Backend()


@app.route('/api/scenario')
def list_scenario():
    return marshal(backend.list_scenarios())


@app.route('/api/scenario/<name>')
def load_scenario(name):
    return marshal(backend.load_scenario(name))


@app.route('/api/scenario/<name>/<modality>')
def load_signals(name, modality):
    return marshal(backend.load_modality(name, modality))


@app.route('/api/scenario/<scenario_id>/<modality>/<signal>', methods=['POST'])
def save_signal(scenario_id, modality, signal):
    signal_json = request.get_data(as_text=True)
    backend.save_signal(scenario_id, unmarshal(signal_json))

    return {}, 200
