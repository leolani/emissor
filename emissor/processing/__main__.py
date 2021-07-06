from enum import Enum, auto

import argparse
import logging
import os
from typing import Any

import emissor.processing.util as processing


class Step(Enum):
    PREPROCESSING = auto()
    INIT = auto()
    PROCESS = auto()


def arg(step: Step) -> str:
    return '--' + step.name.lower().replace('_', '-')


def arg_val(step: Step, args: argparse.Namespace) -> Any:
    return vars(args)[step.name.lower()]


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    parser = argparse.ArgumentParser(description='EMISSOR data processing')
    parser.add_argument('--plugins', type=str, action="append", help="Path to plugin directory (parent of emissor/plugins) ")
    parser.add_argument('--scenarios', type=str, help="Base directory that contains the emissor scenarios.")
    parser.add_argument('--num-jobs', type=int, default=1, help="Max number of parallel processes")

    # Processing steps
    for step in [Step.PREPROCESSING, Step.INIT]:
        parser.add_argument(arg(step), action="store_true", help=f"Execute step {step.name}")

    parser.add_argument(arg(Step.PROCESS), type=str, action="append", help="Execute step PROCESS with SignalProcessor with name PROCESS")

    args, _ = parser.parse_known_args()

    logging.info("Run processing with %s", args)

    plugins = processing.discover_plugins(os.path.abspath(plugin) for plugin in args.plugins)
    data_processing = processing.from_plugins(plugins, args.scenarios,
                            arg_val(Step.PREPROCESSING, args), arg_val(Step.INIT, args), arg_val(Step.PROCESS, args),
                            args.num_jobs)
    data_processing.run()
