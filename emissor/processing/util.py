import argparse
import importlib
import logging
import pkgutil
from inspect import getmembers, isclass
from typing import List, Any

import emissor
import emissor.plugins
from emissor.persistence import ScenarioStorage
from emissor.processing import api
from emissor.processing.processing import DataProcessing, Step

logger = logging.getLogger(__name__)


def discover_plugins() -> List[api.ProcessorPlugin]:
    plugin_itr = pkgutil.iter_modules(emissor.plugins.__path__, emissor.plugins.__name__ + ".")
    plugin_modules = [importlib.import_module(name)
                      for finder, name, ispkg in plugin_itr]

    plugins = [item
               for module in plugin_modules
               for item_name, item in getmembers(module, isclass)
               if issubclass(item, api.ProcessorPlugin)]

    return [plugin() for plugin in sorted(plugins, key=lambda p: p.priority, reverse=True)]


def from_plugins(plugins: List[api.ProcessorPlugin]) -> DataProcessing:
    parser = argparse.ArgumentParser(description='EMISSOR data processing')
    add_args(parser)
    args, _ = parser.parse_known_args()

    logging.info("Run processing with %s", args)

    data_path = args.scenarios
    storage = ScenarioStorage(data_path)

    all_steps = not any(arg_val(step, args) for step in Step)

    preprocessors = [plugin.create_preprocessor() for plugin in plugins] \
        if all_steps or arg_val(Step.PREPROCESSING, args) else []

    initializers = (plugin.create_initializer() for plugin in plugins) \
        if all_steps or arg_val(Step.INIT, args) else []
    initializers = [initializer for initializer in initializers if initializer]

    scenario_initializer = None
    if len(initializers) > 1:
        raise ValueError(f"Multiple ScenarioInitializers found in {plugins}")
    if initializers:
        scenario_initializer = initializers[0]

    processors = arg_val(Step.PROCESS, args)
    if all_steps or processors:
        signal_processors = [processor for plugin in plugins for processor in plugin.create_processors()
                             if not processors or "all" in processors or plugin.name in processors]
    else:
        signal_processors = []

    return DataProcessing(storage, preprocessors, scenario_initializer, signal_processors, args.num_jobs)


def add_args(parser: argparse.ArgumentParser):
    parser.add_argument('--scenarios', type=str, help="Base directory that contains the emissor scenarios.")
    parser.add_argument('--num-jobs', type=int, default=1, help="Max number of parallel processes")

    # Processing steps
    for step in [Step.PREPROCESSING, Step.INIT]:
        parser.add_argument(arg(step), action="store_true")

    parser.add_argument(arg(Step.PROCESS), action="append")


def get_steps(args: argparse.Namespace) -> List[Step]:
    steps = [step for step in Step if arg_val(step, args)]

    return steps if steps else [step for step in Step]


def arg(step: Step) -> str:
    return '--' + step.name.lower().replace('_', '-')


def arg_val(step: Step, args: argparse.Namespace) -> Any:
    return vars(args)[step.name.lower()]