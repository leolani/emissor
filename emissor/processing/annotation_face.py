import argparse
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

from build.lib.emissor.representation.container import MultiIndex
from emissor.annotation.persistence import ScenarioStorage
from emissor.processing.util import DockerInfra
from emissor.representation.annotation import AnnotationType
from emissor.representation.entity import Person
from emissor.representation.scenario import Modality, ImageSignal, Annotation, Mention

IMAGE_DIR = "image"


class Frames2Faces:
    BYTES_AT_LEAST = 256

    # TODO
    def __init__(self, storage: ScenarioStorage, scenario_ids, face_analysis_port, image_ext="jpg",
                 face_cos_distance_threshold=0.8):
        self.scenario_ids = scenario_ids

        self.face_analysis_port = face_analysis_port
        self.image_ext = image_ext
        self.face_cos_distance_threshold = face_cos_distance_threshold

        self.scenario_storage = storage
        self.processing_dir = os.path.join(self.scenario_storage.base_path, "..", "processing")

    def detect_faces(self):
        for scenario_id in tqdm(self.scenario_ids):
            try:
                self.detect_faces_for_scenario(scenario_id)
            except Exception:
                logging.exception("Failed to process %s", scenario_id)

    def detect_faces_for_scenario(self, scenario_id):
        save_path_face_features = os.path.join(self.processing_dir, "face-features", f"{scenario_id}.pkl")

        if os.path.isfile(save_path_face_features) and \
                os.path.getsize(save_path_face_features) > self.BYTES_AT_LEAST:
            logging.info("%s seems to be already done. skipping ...", save_path_face_features)
            return

        signals = self.scenario_storage.load_modality(scenario_id, Modality.IMAGE)

        fa_results_all = []
        for signal in tqdm(signals):
            try:
                assert len(signal.files) == 1
                result = self.image2face(scenario_id, signal.files[0])
                fa_results_all.append((signal, result))
            except Exception:
                logging.exception("Failed to process %s for scenario %s", signal.files[0], scenario_id)

        detection_results = self.face_detection(fa_results_all)
        for signal, face_result, face_id in detection_results:
            self.annotate_signal(scenario_id, signal, face_result, face_id)

    def face_detection(self, results):
        faces = [(signal, face) for signal, result in results for face in result]

        face_ids = self.get_unique_faces([face['normed_embedding'] for _, face in faces])

        return [(face_result[0], face_result[1], face_id) for face_result, face_id in zip(faces, face_ids)]

    def get_unique_faces(self, embeddings):
        logging.debug(f"finding unique faces ...")

        if len(embeddings) == 1:
            labels_clustered = np.array([0])

        elif len(embeddings) == 0:
            return None

        else:
            ac = AgglomerativeClustering(n_clusters=None,
                                         affinity='cosine',
                                         linkage='average',
                                         distance_threshold=self.face_cos_distance_threshold)

            clustering = ac.fit(embeddings)
            labels_clustered = clustering.labels_

        labels_unique = np.unique(labels_clustered)
        while True:
            names_unique = [str(uuid.uuid4()) for _ in labels_unique]
            if len(labels_unique) == len(names_unique):
                break

        label2name = {lbl: nm for lbl, nm in zip(labels_unique, names_unique)}
        face_ids = [label2name[lbl] for lbl in labels_clustered]

        return face_ids

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

    def annotate_signal(self, scenario_id: str, signal: ImageSignal, face_result, face_id):
        age = face_result['age']
        gender = 'male' if face_result['gender'] == 1 else 'female'
        bbox = [int(num) for num in face_result['bbox'].tolist()]
        name = face_id

        image_signal = ImageSignal(signal.id, MultiIndex(signal.ruler.container_id, signal.ruler.bounds), signal.modality, signal.time,
                                   signal.files, signal.mentions, signal.array)
        segment = image_signal.ruler.get_area_bounding_box(*bbox)
        annotation = Annotation(AnnotationType.PERSON.name, Person(uuid.uuid4(), name, age, gender), "cltl.face", int(time.time()))
        mention = Mention(str(uuid.uuid4()), [segment], [annotation])

        signal.mentions.append(mention)

        self.scenario_storage.save_signal(scenario_id, signal)


class ImageProcessing:
    def __init__(self, storage: ScenarioStorage, port_docker_face_analysis: int, num_jobs: int, run_on_gpu: int, image_ext=".jpg"):
        self.num_jobs = num_jobs
        self.image_ext = image_ext
        self.face_infra = DockerInfra('face-analysis-cuda' if run_on_gpu else 'face-analysis',
                                      port_docker_face_analysis, 30000, num_jobs, run_on_gpu, boot_time=30)
        self.scenario_storage = storage

    def extract_face_features(self):
        with self.face_infra:
            scenario_ids = self._get_scenario_ids()
            batch_size = len(scenario_ids) // self.num_jobs
            scenario_batches = [scenario_ids[i:i + batch_size] for i in range(0, len(scenario_ids), batch_size)]

            def extract_faces(*args, **kwargs):
                Frames2Faces(*args, **kwargs).detect_faces()

            logging.debug("face features extraction will begin ...")
            Parallel(n_jobs=self.num_jobs)(delayed(extract_faces)
                                           (self.scenario_storage, scenario_batch, face_analysis_port, self.image_ext)
                                           for scenario_batch, face_analysis_port
                                           in zip(scenario_batches, self.face_infra.host_ports))

            logging.info("face feature extraction complete!")

    def _get_scenario_ids(self):
        scenario_ids = self.scenario_storage.list_scenarios()
        logging.info(
            f"There is a total of {len(scenario_ids)} scenarios found in {self.scenario_storage.base_path}")

        return scenario_ids


def main(storage: ScenarioStorage, port_docker_face_analysis: int, num_jobs: int, run_on_gpu: bool):
    kwargs = {'port_docker_face_analysis': port_docker_face_analysis,
              'run_on_gpu': run_on_gpu,
              'num_jobs': num_jobs}
    vp = ImageProcessing(storage, **kwargs)
    vp.extract_face_features()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    parser = argparse.ArgumentParser(
        description='extract features from a multimodal dataset')
    parser.add_argument('--dataset', type=str)

    parser.add_argument('--port-docker-face-analysis', type=int,
                        default=10002)

    parser.add_argument('--width-max', type=int, default=10000)
    parser.add_argument('--height-max', type=int, default=10000)

    parser.add_argument('--num-jobs', type=int, default=1)
    parser.add_argument('--run-on-gpu', action='store_true')

    args = parser.parse_args()
    args = vars(args)

    logging.info(f"arguments given to {__file__}: {args}")

    main(**args)
