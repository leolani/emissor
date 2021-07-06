import jsonpickle
import logging
import numpy as np
import os
import requests
import time
import uuid
from joblib import Parallel, delayed
from sklearn.cluster import AgglomerativeClustering
from tqdm import tqdm
from typing import Iterable, Mapping

from emissor.persistence import ScenarioStorage
from emissor.processing.api import SignalProcessor
from emissor.representation.annotation import AnnotationType
from emissor.representation.container import MultiIndex
from emissor.representation.entity import Person
from emissor.representation.scenario import Modality, ImageSignal, Annotation, Mention, Scenario, Signal
from example_processing.meld.emissor.plugins.meld.docker import DockerInfra
from example_processing.meld.emissor.plugins.meld.friends import FRIENDS


class MeldFaceProcessor(SignalProcessor):
    BYTES_AT_LEAST = 256

    def __init__(self, port_docker_face_analysis: int, run_on_gpu: int, face_cos_distance_threshold: float):
        self.face_infra = DockerInfra('face-analysis-cuda' if run_on_gpu else 'face-analysis',
                                      port_docker_face_analysis, 30000, run_on_gpu, 30)
        self.face_cos_distance_threshold = face_cos_distance_threshold

    @property
    def parallel(self) -> bool:
        return True

    def __enter__(self):
        self.face_infra.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.face_infra.__exit__(exc_type, exc_val, exc_tb)

    def process(self, scenario: Scenario, signals: Mapping[Modality, Iterable[Signal]], storage: ScenarioStorage):
        logging.debug("Face features extraction will begin ...")
        image_signals = tuple(signals[Modality.IMAGE.name.lower()])
        self.detect_faces_for_scenario(scenario.id, image_signals, storage)
        logging.info("Face feature extraction complete!")

    def detect_faces_for_scenario(self, scenario_id: str, signals: Iterable[Signal], storage: ScenarioStorage):
        # TODO do we want to store these?
        # save_path_face_features = os.path.join(self.processing_dir, "face-features", f"{self.scenario_id}.pkl")
        #
        # if os.path.isfile(save_path_face_features) and \
        #         os.path.getsize(save_path_face_features) > self.BYTES_AT_LEAST:
        #     logging.info("%s seems to be already done. skipping ...", save_path_face_features)
        #     return
        fa_results_all = []
        for signal in tqdm(signals):
            try:
                assert len(signal.files) == 1
                result = self.image2face(scenario_id, signal.files[0], storage)
                fa_results_all.append((signal, result))
            except Exception:
                logging.exception("Failed to process %s for scenario %s", signal.files[0], scenario_id)

        detection_results = self.face_detection(fa_results_all)
        for signal, face_result, face_id in detection_results:
            self.annotate_signal(signal, face_result, face_id)

        storage.save_signals(scenario_id, Modality.IMAGE, signals)

    def face_detection(self, results):
        faces = [(signal, face) for signal, result in results for face in result]

        face_ids = self.get_unique_faces([face['normed_embedding'] for _, face in faces])

        return [(face_result[0], face_result[1], face_id) for face_result, face_id in zip(faces, face_ids)]

    def get_unique_faces(self, embeddings):
        logging.debug(f"finding unique faces ...")

        friends, representations = zip(*FRIENDS.items())

        if len(embeddings) == 0:
            return None
        # elif len(embeddings) == 1:
        #     labels_clustered = np.array([0])
        else:
            ac = AgglomerativeClustering(n_clusters=None,
                                         affinity='cosine',
                                         linkage='average',
                                         distance_threshold=self.face_cos_distance_threshold)

            clustering = ac.fit(representations + tuple(embeddings))
            friend_labels = clustering.labels_[:len(friends)]
            labels_clustered = clustering.labels_[len(friends):]

        friend_labels = {label: friend for friend, label in zip(friends, friend_labels)}
        labels_unique = np.unique(labels_clustered)
        label2name = {label: friend_labels[label] if label in friend_labels else str(uuid.uuid4())
                      for label in labels_unique}

        face_ids = [label2name[label] for label in labels_clustered]

        return face_ids[len(friends):]

    def image2face(self, scenario_id, image_path, storage: ScenarioStorage):
        logging.info("Processing image %s", image_path)

        path = os.path.join(storage.base_path, scenario_id, image_path)
        with open(path, 'rb') as stream:
            data = stream.read()

        data = jsonpickle.encode({'image': data})
        response = requests.post(
            f"{'http://127.0.0.1'}:{self.face_infra.host_port}/", json=data)
        if response.ok:
            logging.info("%s received", response)
        else:
            raise ValueError(f"{response} received with reason {response.reason}")

        response = jsonpickle.decode(response.text)

        return response['fa_results']

    def annotate_signal(self, signal: ImageSignal, face_result, face_id):
        age = face_result['age']
        gender = 'male' if face_result['gender'] == 1 else 'female'
        bbox = [int(num) for num in face_result['bbox'].tolist()]
        name = face_id
        representation = face_result['normed_embedding']

        # segment = signal.ruler.get_area_bounding_box(*bbox)
        segment = MultiIndex(signal.ruler.container_id, bbox)
        annotation_person = Annotation(AnnotationType.PERSON.name, Person(str(uuid.uuid4()), name, age, gender), MeldFaceProcessor.name, int(time.time()))
        annotation_representation = Annotation(AnnotationType.REPRESENTATION.name, representation.tolist(), MeldFaceProcessor.name, int(time.time()))
        mention = Mention(str(uuid.uuid4()), [segment], [annotation_person, annotation_representation])

        signal.mentions.append(mention)
