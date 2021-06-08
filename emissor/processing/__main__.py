import os
from enum import Enum, auto

import argparse
import logging

import emissor.processing.annotation_token_ner as token_ner
import emissor.processing.annotation_entity_linking as entity_linking
import emissor.processing.annotation_face as face_detection
import emissor.processing.annotation_knowledge as ekg

from emissor.annotation.persistence import ScenarioStorage
from emissor.processing.preprocessing import VideoProcessing, TextProcessing
from emissor.representation.scenario import Modality
from .init import run_init


_DEFAULT_MODALITIES = {
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
}


class Step(Enum):
    @property
    def arg(self):
        return '--' + self.name.lower().replace('_', '-')

    PREPROCESSING = auto()
    INIT = auto()
    ANNOTATION_NER = auto()
    ANNOTATION_LINK = auto()
    ANNOTATION_FACE = auto()
    ANNOTATION_EKG = auto()


def main(args):
    all_steps = not any([vars(args)[step.name.lower()] for step in Step])

    emissor_data_path = os.path.join(args.dataset)

    if all_steps or args.preprocessing:
        kwargs = {'port_docker_video2frames': args.port_docker_video2frames,
                  'width_max': args.width_max,
                  'height_max': args.height_max,
                  'fps_max': args.fps_max,
                  'run_on_gpu': args.run_on_gpu,
                  'num_jobs': args.num_jobs,
                  'video_ext': args.video_ext}
        VideoProcessing(args.dataset, **kwargs).split_video()
        TextProcessing(args.dataset).copy_text()

        emissor_data_path = os.path.join(emissor_data_path, "scenarios")

    storage = ScenarioStorage(emissor_data_path, mode=args.init_mode)

    if all_steps or args.init:
        run_init(storage)
    if all_steps or args.annotation_ner:
        token_ner.annotate_scenarios(storage)
    if all_steps or args.annotation_link:
        entity_linking.annotate_scenarios(storage)
    if all_steps or args.annotation_face:
        face_detection.main(storage, args.port_docker_face_analysis, args.num_jobs, args.run_on_gpu)
    if all_steps or args.annotation_ekg:
        ekg.annotate_scenarios(storage)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    parser = argparse.ArgumentParser(description='Setup EMISSOR metadata for a dataset.')
    parser.add_argument('--dataset', type=str, help="Base directory that contains the dataset.")

    # Processing steps
    for step in Step:
        parser.add_argument(step.arg, action="store_true")

    parser.add_argument('--init-mode', type=str, default="metadata")

    # Video preprocessing
    parser.add_argument('--port-docker-video2frames', type=int,
                        default=10001)
    parser.add_argument('--video-ext', type=str, default=".mp4")
    parser.add_argument('--width-max', type=int, default=10000)
    parser.add_argument('--height-max', type=int, default=10000)
    parser.add_argument('--fps-max', type=int, default=10000)
    parser.add_argument('--num-jobs', type=int, default=1)
    parser.add_argument('--run-on-gpu', action='store_true')

    # Face detection
    parser.add_argument('--port-docker-face-analysis', type=int,
                        default=10002)

    args = parser.parse_args()

    logging.info("Run processing with %s", args)

    main(args)

