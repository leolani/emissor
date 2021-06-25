from glob import glob
from os import PathLike

import json
import jsonpickle
import logging
import os
import random
import requests
import shutil
from joblib import Parallel, delayed
from pathlib import Path
from tqdm import tqdm

from emissor.processing.api import DataPreprocessor
from emissor.representation.scenario import Modality
from example_processing.meld.emissor.plugins.mmsr.docker import DockerInfra

IMAGE_DIR = "image"


class Video2Frames:
    BYTES_AT_LEAST = 256

    def __init__(self, dataset, scenarios, video_paths, video2frames_port, fps_max, width_max, height_max, video_ext,
                 image_ext):
        self.dataset = dataset
        self.scenarios = scenarios
        self.video_paths = video_paths
        self.video2frames_port = video2frames_port
        self.fps_max = fps_max
        self.width_max = width_max
        self.height_max = height_max
        self.video_ext = video_ext
        self.image_ext = image_ext

        self.processing_dir = os.path.join(self.dataset, "processing", "frames")

    def split_videos(self):
        for video_path in tqdm(self.video_paths):
            try:
                self.video2frames(video_path)
            except Exception:
                logging.exception("Failed to process %s", video_path)

    def video2frames(self, video_path):
        basename = os.path.basename(video_path)
        video_id = basename.split(f'{self.video_ext}')[0]
        scenario_id = video_id.split("_")[0]

        save_path_metadata = os.path.join(self.processing_dir, f"{scenario_id}/{video_id}.json")

        if os.path.isfile(save_path_metadata) and os.path.getsize(save_path_metadata) > self.BYTES_AT_LEAST:
            logging.debug("%s, %s, seems to be already done. skipping ...", video_path, save_path_metadata)
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
            file_name = os.path.join(self.scenarios, scenario_id, IMAGE_DIR, f"{video_id}_{idx:06d}{self.image_ext}")
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, 'wb') as stream:
                stream.write(frame_bytestring)


class VideoProcessing:
    def __init__(self, dataset, scenarios, run_on_gpu, port_docker_video2frames, width_max, height_max, fps_max,
                 num_jobs, video_ext, image_ext):
        self.dataset = dataset
        self.scenarios = scenarios

        self.video_infra = DockerInfra('video2frames', port_docker_video2frames, 20000, run_on_gpu, 5)
        self.num_jobs = num_jobs
        self.width_max = width_max
        self.height_max = height_max
        self.fps_max = fps_max

        self.image_ext = image_ext
        self.video_ext = video_ext

    def split_video(self):
        video_paths = self._get_video_paths()
        if len(video_paths) == 0:
            raise ValueError(f"No videos found! (ext: {self.video_ext})")

        batch_size = len(video_paths) // self.num_jobs
        video_batches = [video_paths[i:i + batch_size] for i in range(0, len(video_paths), batch_size)]

        def split_videos(*args, **kwargs):
            Video2Frames(*args, **kwargs).split_videos()

        logging.debug("splitting videos will begin ...")
        Parallel(n_jobs=self.num_jobs)(
            delayed(split_videos)(self.dataset, self.scenarios, video_paths, self.video_infra.host_port, self.fps_max,
                                  self.width_max, self.height_max, self.video_ext, self.image_ext)
            for video_paths in video_batches)

        logging.info("splitting videos complete!")

    def _get_video_paths(self):
        video_paths = glob(f'./{self.dataset}/raw-videos/*{self.video_ext}')
        random.shuffle(video_paths)

        logging.info("There is a total of %s videos found in %s", len(video_paths), self.dataset)

        return video_paths


class TextProcessing:
    def __init__(self, dataset, scenarios):
        self._dataset = dataset
        self._scenarios = scenarios

    def copy_text(self):
        logging.info("Copying text from %s/raw-texts/*.json to %s", self._dataset, self._scenarios)

        for text in tqdm(glob(f"{self._dataset}/raw-texts/*.json")):
            path = Path(text)
            scenario_id = path.stem.split('_')[0]
            text_dir = os.path.join(self._scenarios, scenario_id, Modality.TEXT.name.lower())
            os.makedirs(text_dir, exist_ok=True)
            shutil.copyfile(text, os.path.join(text_dir, path.name))

            logging.debug("Copy %s to %s", text, text_dir)


class MMSRMeldPreprocessor(DataPreprocessor):
    """
    Expected directory structure of the dataset:

    dataset
      |- raw-videos
        |- dia{cnt}_utt{cnt}.mp4
        |- dia{cnt}_utt{cnt}.mp4
        |- ...
      |- raw-audios
        |- dia{cnt}_utt{cnt}.wav
        |- dia{cnt}_utt{cnt}.wav
        |- ...
      |- raw-text
        |- dia{cnt}_utt{cnt}.json
        |- dia{cnt}_utt{cnt}.json
        |- ...

    produces:

    dataset
      |- processing
        |- frames
          |- dia{cnt}_utt{cnt}.json
          |- dia{cnt}_utt{cnt}.json
          |- ...
    scenarios
      |- dia{cnt}
        |- images
          |- dia{cnt}_utt{cnt}_{frame}.jpg
          |- ...
        |- text
          |- dia{cnt}_utt{cnt}.json
          |- ...
      |- dia{cnt}
        |- images
          |- dia{cnt}_utt{cnt}_{frame}.jpg
          |- ...
        |- text
          |- dia{cnt}_utt{cnt}.json
          |- ...
    """

    def __init__(self, dataset, scenarios, port_docker_video2frames, width_max, height_max, fps_max, num_jobs,
                 run_on_gpu, video_ext, image_ext):
        self.tp = TextProcessing(dataset, scenarios)
        self.vp = VideoProcessing(dataset=dataset,
                                  scenarios=scenarios,
                                  port_docker_video2frames=port_docker_video2frames,
                                  width_max=width_max,
                                  height_max=height_max,
                                  fps_max=fps_max,
                                  run_on_gpu=run_on_gpu,
                                  num_jobs=num_jobs,
                                  video_ext=video_ext,
                                  image_ext=image_ext)

    def __enter__(self):
        self.vp.video_infra.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.vp.video_infra.__exit__(exc_type, exc_val, exc_tb)

    def preprocess(self):
        self.vp.split_video()
        self.tp.copy_text()
