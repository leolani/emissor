import argparse
import json
import logging
import os
import pickle
import random
from glob import glob

import jsonpickle
import requests
from joblib import Parallel, delayed
from tqdm import tqdm

from emissor.annotation.persistence import ScenarioStorage
from emissor.processing.util import DockerInfra
from emissor.representation.scenario import Modality

IMAGE_DIR = "image"


class Frames2Faces:
    BYTES_AT_LEAST = 256

    def __init__(self, dataset, scenario_ids, face_analysis_port, image_ext="jpg"):
        self.dataset = dataset
        self.scenario_ids = scenario_ids
        self.face_analysis_port = face_analysis_port
        self.image_ext = image_ext

        self.scenario_storage = ScenarioStorage(os.path.join(self.dataset, "scenarios"))
        self.base_dir = os.path.join(self.dataset, "scenarios")
        self.processing_dir = os.path.join(self.dataset, "processing")

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

        signals = self.scenario_storage.load_modality(Modality.IMAGE)

        fa_results_all = []
        for signal in tqdm(signals):
            try:
                assert len(signal.files) == 1
                result = self.image2face(signal.files[0])
                fa_results_all.append(result)
            except Exception:
                logging.exception("Failed to process %s", image_path)

        save_path_face_features = os.path.join(self.processing_dir, "face-features", f"{scenario_id}.pkl")
        os.makedirs(os.path.dirname(save_path_face_features), exist_ok=True)
        with open(save_path_face_features, 'wb') as stream:
            pickle.dump(fa_results_all, stream)

    def image2face(self, image_path):
        logging.info("Processing image %s", image_path)

        with open(image_path, 'rb') as stream:
            data = stream.read()

        data = jsonpickle.encode({'image': data})
        response = requests.post(
            f"{'http://127.0.0.1'}:{self.face_analysis_port}/", json=data)
        logging.info("%s received", response)

        response = jsonpickle.decode(response.text)

        return response['fa_results']

    def annotate_write_frames(self, starttime_msec, SPLIT, diaid, uttid,
                              emotion, frames, fps_original, face_features,
                              frame_idx_original):
            for i, feat in enumerate(ff):
                # age / gender estimation is too poor.
                age = feat['age']
                gender = 'male' if feat['gender'] == 1 else 'female'
                bbox = [int(num) for num in feat['bbox'].tolist()]
                faceprob = round(feat['det_score'], 3)
                name = self.face_names_dia[uttid][idx][i]

                annotations = []
                # emotions are not displayed nicely at the moment.
                # if k == 0:
                #     annotations.append({'source': 'human',
                #                         'timestamp': frame_time,
                #                         'type': 'emotion',
                #                         'value': emotion})

                annotations.append({'source': 'machine',
                                    'timestamp': frame_time,
                                    'type': 'person',
                                    'value': {'name': name,
                                              'age': age,
                                              'gender': gender,
                                              'faceprob': faceprob}})

                mention_id = str(uuid.uuid4())
                segment = [{'bounds': bbox,
                            'container_id': container_id,
                            'type': 'MultiIndex'}]
                frame_info['mentions'].append({'annotations': annotations,
                                               'id': mention_id,
                                               'segment': segment})
            image_emissor_utt.append(frame_info)







class Emissor():
    def __init__(self, dataset, diaids, video2frames_port,
                 port_docker_video2frames, face_prob_threshold,
                 face_cos_distance_threshold, width_max, height_max, fps_max,
                 utterance_ordered, emotions):
        self.dataset = dataset
        self.diaids = diaids

        self.video2frames_port = video2frames_port
        logging.debug(f"creating video2frames container, {self.video2frames_port} "
                      f"to  {port_docker_video2frames}...")
        self.container = \
            docker.run(image='video2frames', detach=True,
                       publish=[(self.video2frames_port, port_docker_video2frames)])
        logging.info(f"video2frames container created!")

        self.face_prob_threshold = face_prob_threshold
        self.face_cos_distance_threshold = face_cos_distance_threshold
        self.width_max = width_max
        self.height_max = height_max
        self.fps_max = fps_max
        self.utterance_ordered = utterance_ordered
        self.emotions = emotions

    def face_recognition_dia(self, scenario_id):
        logging.info(f"running face recognition on {scenario_id}")
        face_features_dia = {}
        face_metadata_dia = {}
        embs_dia = {}

        logging.debug(f"{scenario_id} has {len(self.utterance_ordered[SPLIT][scenario_id])} "
                      f"utterance(s)")
        for uttid in self.utterance_ordered[SPLIT][scenario_id]:
            try:
                face_features_path = self.paths['face-features'][SPLIT][uttid]
                face_metadata_path = self.paths['face-features-metadata'][SPLIT][uttid]

                with open(face_features_path, 'rb') as stream:
                    face_features = pickle.load(stream)

                with open(face_metadata_path, 'r') as stream:
                    face_metadata = json.load(stream)

                assert len(face_features) == face_metadata['num_frames_original'], \
                    f"something ain't right."

            except Exception as e:
                logging.warning(f"{e}: no face info for {uttid}!")
                continue

            face_features_dia[uttid] = face_features
            face_metadata_dia[uttid] = face_metadata

            embs_utt = [[f['normed_embedding'] for f in ff]
                        for ff in face_features]
            embs_dia[uttid] = embs_utt

        # Changed in version 3.7: Dictionary order is guaranteed to be insertion order.
        # This behavior was an implementation detail of CPython from 3.6.
        embs_unpacked = []
        for i, (uttid, embs_utt) in enumerate(embs_dia.items()):
            for j, embs in enumerate(embs_utt):
                for k, emb in enumerate(embs):
                    embs_unpacked.append(emb)

        unique_faces_unpacked = get_unique_faces(embs_unpacked,
                                                 self.face_cos_distance_threshold)

        if unique_faces_unpacked is None:
            self.face_names_dia = None
        else:
            self.face_names_dia = {}
            count = 0
            for i, (uttid, embs_utt) in enumerate(embs_dia.items()):
                self.face_names_dia[uttid] = []
                for j, embs in enumerate(embs_utt):
                    faces_per_frame = []
                    for k, emb in enumerate(embs):
                        unique_name = unique_faces_unpacked[count]
                        faces_per_frame.append(unique_name)
                        count += 1
                    self.face_names_dia[uttid].append(faces_per_frame)

            assert len(embs_unpacked) == len(unique_faces_unpacked) == count

    def load_images_utt(self, SPLIT, uttid):
        """Utterance level. This is the most atomic level."""
        if self.paths['raw-videos'] is not None:
            video_path = self.paths['raw-videos'][SPLIT][uttid]
        else:
            video_path = None
        frames, duration_msec, fps_original, face_features, frame_idx_original = \
            None, None, None, None, None

        if video_path is not None:
            try:
                with open(video_path, 'rb') as stream:
                    binary_video = stream.read()

                data = {'fps_max': self.fps_max, 'width_max': self.width_max,
                        'height_max': self.height_max, 'video': binary_video}
                data = jsonpickle.encode(data)

                response = requests.post(
                    f"{'http://127.0.0.1'}:{self.video2frames_port}/", json=data)
                response = jsonpickle.decode(response.text)
                frames = response['frames']
                metadata = response['metadata']

                frame_idx_original = metadata['frame_idx_original']

                assert len(frames) == len(frame_idx_original)

                logging.debug(f"decompressing frames ...")
                frames = [Image.open(io.BytesIO(frame)) for frame in frames]
                duration_msec = metadata['duration_seconds'] * 1000
                fps_original = metadata['fps_original']
            except Exception as e:
                frames, duration_msec, fps_original, face_features, frame_idx_original = \
                    None, None, None, None, None
                logging.error(f"{e}: no video information on {video_path}!")

        if frames is not None:
            face_features_path = self.paths['face-features'][SPLIT][uttid]
            if video_path is not None and face_features_path is not None:
                with open(face_features_path, 'rb') as stream:
                    face_features = pickle.load(stream)
                face_features = [face_features[idx]
                                 for idx in metadata['frame_idx_original']]
                assert len(frames) == len(
                    face_features), f"{len(frames)}, {len(face_features)}"

                face_features = [[ff for ff in face_feature
                                  if ff['det_score'] > self.face_prob_threshold]
                                 for face_feature in face_features]

        return frames, duration_msec, fps_original, face_features, frame_idx_original

    def annotate_write_frames(self, starttime_msec, SPLIT, diaid, uttid,
                              emotion, frames, fps_original, face_features,
                              frame_idx_original):
        image_emissor_utt = []

        assert len(face_features) == len(frame_idx_original) == len(frames)

        for idx, frame, ff in zip(frame_idx_original, frames, face_features):
            frame_time = int(round(starttime_msec + idx / fps_original*1000))
            os.makedirs(os.path.join(
                self.dataset, 'emissor', SPLIT, diaid, 'image'),
                exist_ok=True)
            save_path = os.path.join(
                self.dataset, 'emissor', SPLIT, diaid, 'image',
                uttid + f'_frame{str(idx)}_{str(frame_time)}.jpg')
            frame.save(save_path)

            frame_info = {}
            frame_info['files'] = [os.path.join(
                'image', os.path.basename(save_path))]
            container_id = str(uuid.uuid4())
            frame_info['id'] = container_id
            frame_info['mentions'] = []

            frame_info['modality'] = 'image'
            frame_info['ruler'] = {'bounds': [0, 0, frame.size[0],
                                              frame.size[1]],
                                   'container_id': container_id,
                                   'type': 'MultiIndex'}
            frame_info['time'] = {'container_id': container_id,
                                  'start': frame_time,
                                  'end': frame_time + int(round(1000/fps_original)),
                                  'type': 'TemporalRuler'}
            frame_info['type'] = 'ImageSignal'

            for i, feat in enumerate(ff):
                # age / gender estimation is too poor.
                age = feat['age']
                gender = 'male' if feat['gender'] == 1 else 'female'
                bbox = [int(num) for num in feat['bbox'].tolist()]
                faceprob = round(feat['det_score'], 3)
                name = self.face_names_dia[uttid][idx][i]

                annotations = []
                # emotions are not displayed nicely at the moment.
                # if k == 0:
                #     annotations.append({'source': 'human',
                #                         'timestamp': frame_time,
                #                         'type': 'emotion',
                #                         'value': emotion})

                annotations.append({'source': 'machine',
                                    'timestamp': frame_time,
                                    'type': 'person',
                                    'value': {'name': name,
                                              'age': age,
                                              'gender': gender,
                                              'faceprob': faceprob}})

                mention_id = str(uuid.uuid4())
                segment = [{'bounds': bbox,
                            'container_id': container_id,
                            'type': 'MultiIndex'}]
                frame_info['mentions'].append({'annotations': annotations,
                                               'id': mention_id,
                                               'segment': segment})
            image_emissor_utt.append(frame_info)

        return image_emissor_utt

    def write_image_emissor(self, SPLIT, diaid, image_emissor_dia):
        os.makedirs(os.path.join(
            self.dataset, 'emissor', SPLIT, diaid, 'image'), exist_ok=True)

        with open(os.path.join(self.dataset, 'emissor', SPLIT, diaid,
                               'image.json'), 'w') as stream:
            json.dump(image_emissor_dia, stream, indent=4)









class ImageProcessing:
    def __init__(self, dataset, port_docker_face_analysis, num_jobs, run_on_gpu, image_ext=".jpg"):
        self.dataset = dataset
        self.num_jobs = num_jobs
        self.image_ext = image_ext
        self.face_infra = DockerInfra('face-analysis-cuda' if run_on_gpu else 'face-analysis',
                                      port_docker_face_analysis, 30000, num_jobs, run_on_gpu, boot_time=30)
        self.scenario_storage = ScenarioStorage(os.path.join(self.dataset, "scenarios"))

    def extract_face_features(self):
        with self.face_infra:
            scenario_ids = self._get_scenario_ids()
            batch_size = len(scenario_ids) // self.num_jobs
            scenario_batches = [scenario_ids[i:i + batch_size] for i in range(0, len(scenario_ids), batch_size)]

            def extract_faces(*args, **kwargs):
                Frames2Faces(*args, **kwargs).detect_faces()

            logging.debug("face features extraction will begin ...")
            Parallel(n_jobs=self.num_jobs)(delayed(extract_faces)
                                           (self.dataset, scenario_batch, face_analysis_port, self.image_ext)
                                           for scenario_batch, face_analysis_port
                                           in zip(scenario_batches, self.face_infra.host_ports))

            logging.info("face feature extraction complete!")

    def _get_scenario_ids(self):
        scenario_ids = self.scenario_storage.list_scenarios()
        logging.info(
            f"There is a total of {len(scenario_ids)} scenarios found in {self.dataset}")

        return scenario_ids


def main(dataset, port_docker_face_analysis, num_jobs, face_features, run_on_gpu):
    kwargs = {'port_docker_face_analysis': port_docker_face_analysis,
              'run_on_gpu': run_on_gpu,
              'num_jobs': num_jobs}
    vp = ImageProcessing(dataset, **kwargs)
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

    parser.add_argument('--port-docker-video2frames', type=int,
                        default=10001)
    parser.add_argument('--port-docker-face-analysis', type=int,
                        default=10002)

    parser.add_argument('--face-features', action='store_true')
    parser.add_argument('--face-videos', action='store_true')
    parser.add_argument('--visual-features', action='store_true')
    parser.add_argument('--width-max', type=int, default=10000)
    parser.add_argument('--height-max', type=int, default=10000)
    parser.add_argument('--fps-max', type=int, default=10000)

    parser.add_argument('--audio-features', action='store_true')
    parser.add_argument('--text-features', action='store_true')

    parser.add_argument('--num-jobs', type=int, default=1)
    parser.add_argument('--run-on-gpu', action='store_true')

    args = parser.parse_args()
    args = vars(args)

    logging.info(f"arguments given to {__file__}: {args}")

    main(**args)
