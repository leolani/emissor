from enum import Enum, auto

import argparse
import logging

from emissor.representation.scenario import Modality
from .init import run_init


_DEFAULT_MODALITIES = {
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
}


class Step(Enum):
    @property
    def arg(self):
        return '--' + self.name.lower()

    INIT = auto()
    MODALITY = auto()
    ANNOTATION = auto()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup EMISSOR metadata for a dataset.')
    parser.add_argument(Step.INIT.arg , action="store_true")
    parser.add_argument('--dataset', type=str,
                        help="Base directory that contains the scenarios of the dataset.")

    args = parser.parse_args()
    logging.info("Setting up EMISSOR for dataset %s", args.dataset)

    all_steps = not any([args[step.name.lower()] for step in Step])

    if all_steps or args['preprocessing']:
        raise NotImplementedError("")

    if all_steps or args['setup']:
        run_init(args.dataset)

