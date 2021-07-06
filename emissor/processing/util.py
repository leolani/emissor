import importlib
import logging
import pkgutil
import sys
from inspect import getmembers, isclass
from typing import List, Iterable

import emissor
import emissor.plugins
from emissor.persistence import ScenarioStorage
from emissor.processing import api
from emissor.processing.processing import DataProcessing

logger = logging.getLogger(__name__)


def discover_plugins(plugin_paths: Iterable[str]) -> List[api.ProcessorPlugin]:
    for path in plugin_paths:
        sys.path.append(path)

    plugin_itr = pkgutil.iter_modules(emissor.plugins.__path__, emissor.plugins.__name__ + ".")
    plugin_modules = [importlib.import_module(name)
                      for finder, name, ispkg in plugin_itr]

    plugins = [item
               for module in plugin_modules
               for item_name, item in getmembers(module, isclass)
               if issubclass(item, api.ProcessorPlugin)]

    return [plugin() for plugin in sorted(plugins, key=lambda p: p.priority, reverse=True)]


def from_plugins(plugins: List[api.ProcessorPlugin], data_path: str,
                 preprocessing: bool, init: bool, processors: List[str], num_jobs: int) -> DataProcessing:
    storage = ScenarioStorage(data_path)

    all_steps = not any([preprocessing, init, processors])

    preprocessors = [plugin.create_preprocessor() for plugin in plugins] \
        if all_steps or preprocessing else []

    initializers = (plugin.create_initializer() for plugin in plugins) \
        if all_steps or init else []
    initializers = [initializer for initializer in initializers if initializer]

    scenario_initializer = None
    if len(initializers) > 1:
        raise ValueError(f"Multiple ScenarioInitializers found in {plugins}")
    if initializers:
        scenario_initializer = initializers[0]

    if all_steps or processors:
        signal_processors = [processor for plugin in plugins for processor in plugin.create_processors()
                             if not processors or "all" in processors or plugin.name in processors]
    else:
        signal_processors = []

    return DataProcessing(storage, preprocessors, scenario_initializer, signal_processors, num_jobs)
