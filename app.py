import sys

import logging
import os

import argparse

from grmc.endpoint import create_app

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
    default_static = os.path.join(app_path, 'data')

    parser = argparse.ArgumentParser(description='Web server for GRMC annotations app')
    parser.add_argument('-data', type=str, default=default_static,
                        help='Path to the directory containing scenario data. Defaults to ./data')
    args = parser.parse_args()

    logger.info("Serve data folder: %s", args.data)

    app = create_app(args.data)
    app.debug = True
    app.run(ssl_context=(os.path.join(app_path, 'cert.pem'), os.path.join(app_path, 'key.pem')),
            threaded=False, processes=1)
