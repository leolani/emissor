from flask import Flask, url_for, request, render_template, redirect, jsonify
import csv
import grmc.backend as backend


app = Flask(__name__)


@app.route('/api/scenarios')
def list_scenario():
    return jsonify(backend.list_scenarios())


@app.route('/api/scenario/<name>')
def load_scenario(name):
    return jsonify(backend.load_scenario(name))


@app.route('/api/scenario/<name>/<modality>')
def load_signals(name, modality):
    return jsonify(backend.load_signals(name, modality))
