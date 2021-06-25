import argparse
import logging

import emissor.processing.util as processing

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    plugins = processing.discover_plugins()
    processing.from_plugins(plugins).run()

