import sys

import logging
import os

import argparse

from emissor.annotation.endpoint import create_app

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app_path = os.path.dirname(os.path.realpath(__file__))
    default_data = os.path.join(app_path, 'data')
    static_path = os.path.join(app_path, 'webapp', 'dist', 'emissor-annotation')

    parser = argparse.ArgumentParser(description='Web server for EMISSOR annotations app')
    parser.add_argument('-data', type=str, default=default_data,
                        help='Path to the directory containing scenario data. Defaults to ./data')
    parser.add_argument('--plugins', type=str, action="append", default=[],
                        help="Path to plugin directory (parent of emissor/plugins) ")
    args = parser.parse_args()

    data = os.path.abspath(args.data)
    logger.info("Serve data folder: %s", data)

    plugins = [os.path.abspath(plugin) for plugin in args.plugins]
    logger.info("Use plugins from: %s", plugins)

    app = create_app(data, static_path, plugins)
    app.debug = True
    app.run(threaded=False, processes=1)
