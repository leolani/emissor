import argparse
import logging
from typing import Iterable

from emissor.processing.api import ProcessorPlugin, DataPreprocessor, SignalProcessor, ScenarioInitializer
from .annotation_entity_linking import MeldEntityLinkingProcessor
from .annotation_face import MeldFaceProcessor
from .annotation_token_ner import MeldNERProcessor
from .init import MeldInitializer
from .preprocessing import MeldPreprocessor

logger = logging.getLogger(__name__)


class MeldExamplePlugin(ProcessorPlugin):
    def __init__(self):
        parser = argparse.ArgumentParser(description=self.name + ' plugin for EMISSOR data processing')

        parser.add_argument('--dataset', type=str, required=True,
                            help="Base directory that contains the dataset.")
        parser.add_argument('--scenarios', type=str, required=True,
                            help="Base directory that contains the scenarios.")

        # Video preprocessing
        parser.add_argument('--port-docker-video2frames', type=int, default=10001)
        parser.add_argument('--video-ext', type=str, default=".mp4")
        parser.add_argument('--width-max', type=int, default=10000)
        parser.add_argument('--height-max', type=int, default=10000)
        parser.add_argument('--fps-max', type=int, default=1)
        parser.add_argument('--num-jobs', type=int, default=1)
        parser.add_argument('--run-on-gpu', action='store_true')

        # Face detection
        parser.add_argument('--port-docker-face-analysis', type=int,
                            default=10002)

        args, _ = parser.parse_known_args()
        logger.info("Initialize %s plugin with %s", self.name, args)

        self.__dict__.update(vars(args))
        self.image_ext = ".jpg"

    def create_preprocessor(self) -> DataPreprocessor:
        return MeldPreprocessor(self.dataset, self.scenarios, self.port_docker_video2frames, self.width_max,
                                self.height_max, self.fps_max, self.num_jobs, self.run_on_gpu, self.video_ext,
                                self.image_ext)

    def create_initializer(self) -> ScenarioInitializer:
        return MeldInitializer(self.dataset)

    def create_processors(self) -> Iterable[SignalProcessor]:
        return [MeldNERProcessor(),
                MeldFaceProcessor(self.scenarios, self.port_docker_face_analysis, self.run_on_gpu, 0.8),
                MeldEntityLinkingProcessor(self.scenarios)]
