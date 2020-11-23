import json
from flask import Flask, jsonify
from flask_cors import CORS

import grmc.backend as backend
from grmc.representation.util import serializer

app = Flask(__name__)
CORS(app)


@app.route('/api/scenario')
def list_scenario():
    return jsonify(backend.list_scenarios())


@app.route('/api/scenario/<name>')
def load_scenario(name):
    return json.dumps(backend.load_scenario(name), default=serializer)


@app.route('/api/scenario/<name>/<modality>')
def load_signals(name, modality):
    return json.dumps(backend.load_modality(name, modality), default=serializer)
