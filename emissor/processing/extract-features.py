import argparse
import json
import logging
import os
import pickle
import random
import time
from glob import glob

import jsonpickle
import requests
from joblib import Parallel, delayed
from python_on_whales import docker
from tqdm import tqdm

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


IMAGE_DIR = "image"


class Video2Frames:
    BYTES_AT_LEAST = 256

    def __init__(self, dataset, video_paths, video2frames_port, fps_max, width_max, height_max, video_ext, image_ext=".jpg"):
        self.dataset = dataset
        self.video_paths = video_paths
        self.video2frames_port = video2frames_port
        self.fps_max = fps_max
        self.width_max = width_max
        self.height_max = height_max
        self.video_ext = video_ext
        self.image_ext = image_ext

        self.base_dir = os.path.join(self.dataset, "scenarios")
        self.processing_dir = os.path.join(self.dataset, "processing")

    def split_videos(self):
        for video_path in tqdm(self.video_paths):
            try:
                self.video2frames(video_path)
            except Exception:
                logging.exception("Failed to process %s", video_path)

    def video2frames(self, video_path):
        basename = os.path.basename(video_path)
        scenario_id = basename.split(f'{self.video_ext}')[0]

        save_path_metadata = os.path.join(self.processing_dir, f"{scenario_id}.json")

        if os.path.isfile(save_path_metadata) and os.path.getsize(save_path_metadata) > self.BYTES_AT_LEAST:
            logging.info("%s, %s, seems to be already done. skipping ...", video_path, save_path_metadata)
            return

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

        os.makedirs(os.path.dirname(save_path_metadata), exist_ok=True)
        with open(save_path_metadata, 'w') as stream:
            json.dump(metadata, stream, indent=4)

        assert len(frames) == len(metadata['frame_idx_original'])

        for frame_bytestring, idx in zip(frames, metadata['frame_idx_original']):
            file_name = os.path.join(self.base_dir, scenario_id, IMAGE_DIR, f"{scenario_id}_{idx:04d}{self.image_ext}")
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, 'wb') as stream:
                stream.write(frame_bytestring)


class Frames2Faces:
    BYTES_AT_LEAST = 256

    def __init__(self, dataset, scenario_ids, face_analysis_port, image_ext="jpg"):
        self.dataset = dataset
        self.scenario_ids = scenario_ids
        self.face_analysis_port = face_analysis_port
        self.image_ext = image_ext

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

        fa_results_all = []
        for image_path in tqdm(glob(os.path.join(self.base_dir, scenario_id, IMAGE_DIR, f"*{self.image_ext}"))):
            try:
                result = self.image2face(image_path)
                fa_results_all.append(result)
            except Exception:
                logging.exception("Failed to process %s", image_path)

        save_path_face_features = os.path.join(self.processing_dir, "face-features", f"{scenario_id}.pkl")
        os.makedirs(os.path.join(self.processing_dir, "face-features"), exist_ok=True)
        with open(save_path_face_features, 'wb') as stream:
            pickle.dump(fa_results_all, stream)

    def image2face(self, image_path):
        logging.info(f"Processing image %s", image_path)
        with open(image_path, 'rb') as stream:
            data = stream.read()

        data = jsonpickle.encode({'image': data})
        response = requests.post(
            f"{'http://127.0.0.1'}:{self.face_analysis_port}/", json=data)
        logging.info(f"{response} received")

        response = jsonpickle.decode(response.text)

        return response['fa_results']


class DockerInfra:
    def __init__(self, image, port, host_ports, num_jobs, run_on_gpu = False, boot_time=30):
        self.image = image
        self.port = port
        self.host_ports = range(host_ports, host_ports + num_jobs)
        self.num_jobs = num_jobs
        self.run_on_gpu = run_on_gpu
        self.boot_time = boot_time

        self.containers = {}

    def start_containers(self):
        if len(self.containers):
            raise EnvironmentError("Containers already started")

        logging.info("Creating %s containers of %s ...", self.num_jobs, self.image)

        self.containers = []
        for i in range(self.num_jobs):
            container = docker.run(image=self.image, detach=True, remove=False, publish=[(self.host_ports[i], self.port)])
            self.containers.append(container)
            logging.debug("sleeping for %s seconds to warm up %s th container for %s ...", self.boot_time, i, self.image)
            time.sleep(self.boot_time)
            logging.debug("sleeping done for %s th container for %s ...", i, self.image)

    def stop_containers(self):
        for container in self.containers:
            logging.info("stopping the container %s of %s ...", container, self.image)
            container.stop()

        self.containers = []


class VideoProcessing:
    def __init__(self, dataset, run_on_gpu, port_docker_video2frames, port_docker_face_analysis, width_max, height_max,
                 fps_max, num_jobs):
        self.dataset = dataset

        self.video_infra = DockerInfra('video2frames', port_docker_video2frames, 20000, num_jobs, run_on_gpu,
                                       boot_time=5)
        self.face_infra = DockerInfra('face-analysis-cuda' if run_on_gpu else 'face-analysis',
                                      port_docker_face_analysis, 30000, num_jobs, run_on_gpu, boot_time=30)
        self.num_jobs = num_jobs
        self.width_max = width_max
        self.height_max = height_max
        self.fps_max = fps_max

        self.image_ext = ".jpg"
        self.video_ext = {'MELD': '.mp4',
                          'IEMOCAP': '.mp4',
                          'CarLani': '.mp4'}[self.dataset]

    def split_video(self):
        self.video_infra.start_containers()

        video_paths = self._get_video_paths()
        if len(video_paths) == 0:
            raise ValueError(f"No videos found!")

        try:
            batch_size = len(video_paths) // self.num_jobs
            video_batches = [video_paths[i:i + batch_size] for i in range(0, len(video_paths), batch_size)]

            def split_videos(*args, **kwargs):
                Video2Frames(*args, **kwargs).split_videos()

            logging.debug("splitting videos will begin ...")
            Parallel(n_jobs=self.num_jobs)(
                delayed(split_videos)(
                    self.dataset, video_paths, video2frames_port, self.fps_max, self.width_max, self.height_max,
                    self.video_ext)
                for video_paths, video2frames_port
                in zip(video_batches, self.video_infra.host_ports))

            logging.info("splitting videos complete!")
        except Exception:
            logging.exception("Failed to split videos")
        finally:
            self.video_infra.stop_containers()

    def extract_face_features(self):
        self.face_infra.start_containers()

        try:
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
        except Exception:
            logging.exception("Failed to extract faces")
        finally:
            self.face_infra.stop_containers()

    def _get_video_paths(self):
        video_paths = glob(f'./{self.dataset}/raw-videos/*/*{self.video_ext}')
        random.shuffle(video_paths)

        logging.info(
            f"There is a total of %s videos found in %s", len(video_paths), self.dataset)

        return video_paths

    def _get_scenario_ids(self):
        scenario_ids = [os.path.basename(s) for s in glob(f'./{self.dataset}/scenarios/*')]

        logging.info(
            f"There is a total of {len(scenario_ids)} scenarios found in {self.dataset}")

        return scenario_ids


def main(dataset, port_docker_video2frames, port_docker_face_analysis, width_max,
         height_max, fps_max, num_jobs, face_features, face_videos,
         visual_features, audio_features, text_features, run_on_gpu):

    if face_features:
        kwargs = {'port_docker_video2frames': port_docker_video2frames,
                  'port_docker_face_analysis': port_docker_face_analysis,
                  'width_max': width_max,
                  'height_max': height_max,
                  'fps_max': fps_max,
                  'run_on_gpu': run_on_gpu,
                  'num_jobs': num_jobs}
        vp = VideoProcessing(dataset, **kwargs)
        vp.split_video()
        vp.extract_face_features()


if __name__ == "__main__":
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
