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
from typing import Iterable

from emissor.persistence import ScenarioStorage
from emissor.processing.api import SignalProcessor
from emissor.representation.annotation import AnnotationType
from emissor.representation.container import MultiIndex
from emissor.representation.entity import Person
from emissor.representation.scenario import Modality, ImageSignal, Annotation, Mention, Scenario, Signal
from example_processing.meld.emissor.plugins.mmsr.docker import DockerInfra
from example_processing.meld.emissor.plugins.mmsr.friends import FRIENDS

IMAGE_DIR = "image"


class Frames2Faces:
    BYTES_AT_LEAST = 256

    def __init__(self, storage: ScenarioStorage, scenario_id, signals, face_analysis_port, image_ext="jpg",
                 face_cos_distance_threshold=0.6):
        self.scenario_id = scenario_id
        self.signals = signals

        self.face_analysis_port = face_analysis_port
        self.image_ext = image_ext
        self.face_cos_distance_threshold = face_cos_distance_threshold

        self.scenario_storage = storage
        self.processing_dir = os.path.join(self.scenario_storage.base_path, "..", "processing")

    def detect_faces_for_scenario(self):
        # TODO do we want to store these?
        # save_path_face_features = os.path.join(self.processing_dir, "face-features", f"{self.scenario_id}.pkl")
        #
        # if os.path.isfile(save_path_face_features) and \
        #         os.path.getsize(save_path_face_features) > self.BYTES_AT_LEAST:
        #     logging.info("%s seems to be already done. skipping ...", save_path_face_features)
        #     return
        fa_results_all = []
        for signal in tqdm(self.signals):
            try:
                assert len(signal.files) == 1
                result = self.image2face(self.scenario_id, signal.files[0])
                fa_results_all.append((signal, result))
            except Exception:
                logging.exception("Failed to process %s for scenario %s", signal.files[0], self.scenario_id)

        detection_results = self.face_detection(fa_results_all)
        for signal, face_result, face_id in detection_results:
            self.annotate_signal(signal, face_result, face_id)

        self.scenario_storage.save_signals(self.scenario_id, Modality.IMAGE, self.signals)

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

    def image2face(self, scenario_id, image_path):
        logging.info("Processing image %s", image_path)

        path = os.path.join(self.scenario_storage.base_path, scenario_id, image_path)
        with open(path, 'rb') as stream:
            data = stream.read()

        data = jsonpickle.encode({'image': data})
        response = requests.post(
            f"{'http://127.0.0.1'}:{self.face_analysis_port}/", json=data)
        logging.info("%s received", response)

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
        annotation_person = Annotation(AnnotationType.PERSON.name, Person(str(uuid.uuid4()), name, age, gender), MMSRMeldFaceProcessor.name, int(time.time()))
        annotation_representation = Annotation(AnnotationType.REPRESENTATION.name, representation.tolist(), MMSRMeldFaceProcessor.name, int(time.time()))
        mention = Mention(str(uuid.uuid4()), [segment], [annotation_person, annotation_representation])

        signal.mentions.append(mention)


class MMSRMeldFaceProcessor(SignalProcessor):
    def __init__(self, port_docker_face_analysis: int, num_jobs: int, run_on_gpu: int, image_ext):
        self.num_jobs = num_jobs
        self.image_ext = image_ext
        self.face_infra = DockerInfra('face-analysis-cuda' if run_on_gpu else 'face-analysis',
                                      port_docker_face_analysis, 30000, num_jobs, run_on_gpu, boot_time=30)

    def __enter__(self):
        self.face_infra.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.face_infra.__exit__(exc_type, exc_val, exc_tb)

    def process(self, scenario: Scenario, modality: Modality, signals: Iterable[Signal], storage: ScenarioStorage):
        if modality is not Modality.IMAGE:
            return

        signals = tuple(signals)
        batch_size = len(signals) // self.num_jobs
        signal_batches = [signals[i:i + batch_size] for i in range(0, len(signals), batch_size)]

        def extract_faces(*args, **kwargs):
            Frames2Faces(*args, **kwargs).detect_faces_for_scenario()

        logging.debug("face features extraction will begin ...")
        Parallel(n_jobs=self.num_jobs)(delayed(extract_faces)
                                       (storage, scenario.id, signal_batch, face_analysis_port, self.image_ext)
                                       for signal_batch, face_analysis_port
                                       in zip(signal_batches, self.face_infra.host_ports))

        logging.info("face feature extraction complete!")
