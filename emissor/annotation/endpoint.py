import os
from flasgger import Swagger
from flask import Flask, request, send_from_directory
from flask_cors import CORS

from emissor.annotation.backend import Backend
from emissor.representation.scenario import Modality
from emissor.representation.util import unmarshal, marshal


def create_app(data_path, static_path):
    app = Flask(__name__, static_url_path='/data', static_folder=data_path)
    Swagger(app)
    CORS(app)

    backend = Backend(data_path)

    # Serving static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<string:path>')
    @app.route('/<path:path>')
    def static_proxy(path):
        if not path:
            path = "index.html"

        return send_from_directory(os.path.abspath(static_path), path)

    @app.route('/api/scenario')
    def list_scenario():
        """Get all scenario IDs
        Lists all subfolders in data folder.
        ---
        tags:
          - scenario
        definitions:
          Scenarios:
            type: array
            items:
              $ref: '#/definitions/Scenario_ID'
          Scenario_ID:
            type: string
        responses:
          200:
            description: A list of scenario IDs
            schema:
              $ref: '#/definitions/Scenarios'
        """
        return marshal(backend.list_scenarios())

    @app.route('/api/scenario/<scenario_id>')
    def load_scenario(scenario_id):
        """Load scenario attributes
        Load scenario file in the given scenario folder
        ---
        tags:
          - scenario
        parameters:
          - name: scenario_id
            in: path
            type: string
            required: true
            default: 'scenario_1'
        definitions:
          Scenario:
            type: object
            properties:
              context:
                $ref: '#/definitions/Context'
              end:
                type: int
              id:
                $ref: '#/definitions/Scenario_ID'
              ruler:
                $ref: '#/definitions/Ruler'
              signals:
                $ref: '#/definitions/Signals'
              start:
                type: int
              type:
                type: string
          Scenario_ID:
            type: string
          Context:
            type: object
            properties:
              agent:
                type: string
              objects:
                type: array
                items:
                  $ref: '#/definitions/Object'
              persons:
                type: array
                items:
                  $ref: '#/definitions/Person'
              speaker:
                $ref: '#/definitions/Speaker'
          Speaker:
            type: object
            properties:
              age:
                type: int
              gender:
                type: string
                enum: ['undefined']
              id:
                type: string
              name:
                type: string
          Ruler:
            type: object
            properties:
              container_id:
                type: string
              end:
                type: int
              start:
                type: int
              type:
                type: string
          Signals:
            type: object
            properties:
              image:
                type: string
              text:
                type: string
          Object:
            type: string
          Person:
            type: string
        responses:
          200:
            description: A scenario and its values
            schema:
              $ref: '#/definitions/Scenario'
        """
        return marshal(backend.load_scenario(scenario_id))

    @app.route('/api/scenario/<scenario_id>/<modality>')
    def load_signals(scenario_id, modality):
        """Load signals in a given modality and scenario
        Load modality file in the given scenario
        ---
        tags:
          - signals
        parameters:
          - name: scenario_id
            in: path
            type: string
            required: true
            default: 'scenario_1'
          - name: modality
            in: path
            type: string
            enum: ['image', 'text', 'audio', 'video']
            required: true
            default: 'text'
        responses:
          200:
            description: List of signals of a specific modality and belonging to a given scenario
        """
        signals = backend.load_modality(scenario_id, Modality[modality.upper()])

        if len(signals) == 0:
            return "[]"

        return marshal(signals, cls=signals[0].__class__)

    @app.route('/api/scenario/<scenario_id>/<modality>/<signal>', methods=['POST'])
    def save_signal(scenario_id, modality, signal):
        """Save signal
        Save a signal related to a specific scenario and modality
        ---
        tags:
          - signals
        parameters:
          - name: scenario_id
            in: path
            type: string
            required: true
            default: 'scenario_1'
          - name: modality
            in: path
            type: string
            enum: ['image', 'text', 'audio', 'video']
            required: true
            default: 'text'
          - name: signal
            in: path
            $ref: '#/definitions/Signals'
            required: true
            default: '4f0bbc71-2369-4d55-8dd0-b00e56c0f0b2'
        responses:
          200:
            description: Successful addition of signal of specific modality to a given scenario
        """
        signal_json = request.get_data(as_text=True)
        backend.save_signal(scenario_id, unmarshal(signal_json))

        return ""

    @app.route('/api/scenario/<scenario_id>/<modality>/<signal_id>/mention', methods=['PUT'])
    def create_mention(scenario_id: str, modality: str, signal_id: str):
        """Create a Mention
        Return a new Mention object related to the given signal, modality and scenario id
        ---
        tags:
          - annotation
        parameters:
          - name: scenario_id
            in: path
            type: string
            required: true
            default: 'scenario_1'
          - name: modality
            in: path
            type: string
            enum: ['image', 'text', 'audio', 'video']
            required: true
            default: 'text'
          - name: signal_id
            in: path
            type: string
            required: true
            default: '4f0bbc71-2369-4d55-8dd0-b00e56c0f0b2'
        responses:
          200:
            description: A Mention in the given signal, of a specific modality and related to a given scenario. The new Mention contains placeholders for annotations and segments
        """
        return marshal(backend.create_mention(scenario_id, Modality[modality.upper()], signal_id))

    @app.route('/api/scenario/<scenario_id>/<modality>/<signal_id>/<mention_id>/annotation', methods=['PUT'])
    def create_annotation(scenario_id: str, modality: str, signal_id: str, mention_id: str):
        """Create an Annotation
        Return a new Annotation object related to the given signal, modality and scenario id
        ---
        tags:
          - annotation
        parameters:
          - name: scenario_id
            in: path
            type: string
            required: true
            default: 'scenario_1'
          - name: modality
            in: path
            type: string
            enum: ['image', 'text', 'audio', 'video']
            required: true
            default: 'text'
          - name: signal_id
            in: path
            type: string
            required: true
            default: '4a6eea5a-5b5a-421d-98e1-c68c74ca3345'
          - name: mention_id
            in: path
            type: string
            required: true
            default: '856472ee-bf95-4876-9081-fea94b710a29'
          - name: type
            in: query
            type: string
            required: true
            default: 'person'
        responses:
          200:
            description: An Annotation in the given signal, of a specific modality and related to a given scenario.
        """
        type_ = request.args.get("type")
        return marshal(backend.create_annotation(type_))

    @app.route('/api/scenario/<scenario_id>/<modality>/<signal_id>/<mention_id>/segment', methods=['PUT'])
    def create_segment(scenario_id: str, modality: str, signal_id: str, mention_id: str):
        """Create an Annotation
        Return a new Annotation object related to the given signal, modality and scenario id
        ---
        tags:
          - annotation
        parameters:
          - name: scenario_id
            in: path
            type: string
            required: true
            default: 'scenario_1'
          - name: modality
            in: path
            type: string
            enum: ['image', 'text', 'audio', 'video']
            required: true
            default: 'text'
          - name: signal_id
            in: path
            type: string
            required: true
            default: '4a6eea5a-5b5a-421d-98e1-c68c74ca3345'
          - name: mention_id
            in: path
            type: string
            required: true
            default: '856472ee-bf95-4876-9081-fea94b710a29'
          - name: type
            in: query
            type: string
            required: true
            default: 'index'
          - name: container
            in: query
            type: string
            required: true
            default: 'e7c7312b-33b8-4b3d-86e4-57a6b4dc2f1c'
        responses:
          200:
            description: A Segment in the given signal, of a specific modality and related to a given scenario.
        """
        type_ = request.args.get("type")
        container_id = request.args.get("container")

        return marshal(
            backend.create_segment(scenario_id, Modality[modality.upper()], signal_id, mention_id, type_, container_id))

    @app.route('/test')
    def test():
        from pprint import pprint
        pprint(app.url_map)

        return str(app.url_map)

    @app.route('/api/scenario/<scenario_id>/annotation/class_types')
    def load_annotation_types(scenario_id: str):
        """Get all potential annotation types based on the ontology
        Lists all class types in the brain.
        ---
        tags:
          - annotation-brain
        parameters:
          - name: scenario_id
            in: path
            type: string
            required: true
            default: 'scenario_1'
        definitions:
          AnnotationTypes:
            type: array
            items:
              $ref: '#/definitions/AnnotationType'
          AnnotationType:
            type: object
            properties:
              full_id:
                type: URI
              prefixed_id:
                type: string
              prefix:
                type: string
              id:
                type: string
        responses:
          200:
            description: A list of classes representing potential annotation types
            schema:
              $ref: '#/definitions/AnnotationTypes'
        """
        return marshal(backend.load_annotation_types())

    @app.route('/api/scenario/<scenario_id>/annotation/relation_types')
    def load_relation_types(scenario_id: str):
        """Get all potential relational annotation types based on the ontology
        Lists all relations types in the brain.
        ---
        tags:
          - annotation-brain
        parameters:
          - name: scenario_id
            in: path
            type: string
            required: true
            default: 'scenario_1'
        definitions:
          AnnotationTypes:
            type: array
            items:
              $ref: '#/definitions/AnnotationType'
          AnnotationType:
            type: object
            properties:
              full_id:
                type: URI
              prefixed_id:
                type: string
              prefix:
                type: string
              id:
                type: string
        responses:
          200:
            description: A list of relation types representing potential annotation types
            schema:
              $ref: '#/definitions/AnnotationTypes'
        """
        return marshal(backend.load_relation_types())

    @app.route('/api/scenario/<scenario_id>/<modality>/<signal_id>/<mention_id>/<annotation_id>/denotedBy')
    def create_denotedBy(scenario_id: str, modality: str, signal_id: str, mention_id: str, annotation_id: str):
        """Create links between signal annotations in brain
        Link mentions to instances by loading the annotations in signals of a given modality in a scenario
        ---
        tags:
          - signals
        parameters:
          - name: scenario_id
            in: path
            type: string
            required: true
            default: 'scenario_1'
          - name: modality
            in: path
            type: string
            enum: ['image', 'text', 'audio', 'video']
            required: true
            default: 'text'
          - name: signal_id
            in: path
            type: string
            required: true
            default: '4f0bbc71-2369-4d55-8dd0-b00e56c0f0b2'
          - name: mention_id
            in: path
            type: string
            required: true
            default: '68fdc43f-cc13-46a9-b9ab-d26abacc8fdb'
          - name: annotation_id
            in: path
            type: string
            required: true
            default: '190cb100-e2c7-4f15-9f2f-8c6f3a73a88f'
        responses:
          200:
            description: Successful addition of the link between mention and an annotation
        """
        return marshal(backend.create_denotations(scenario_id, modality, signal_id, mention_id, annotation_id))

    return app
