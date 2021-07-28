import logging
import time
from python_on_whales import docker

logger = logging.getLogger(__name__)


class DockerInfra:
    def __init__(self, image, port, host_port, run_on_gpu = False, boot_time=10):
        self.image = image
        self.port = port
        self.host_port = host_port
        self.run_on_gpu = run_on_gpu
        self.boot_time = boot_time

        self.container = None

    def __enter__(self):
        self.start_container()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_container()

    def start_container(self):
        if self.container:
            raise EnvironmentError("Container already started")

        logger.info("Creating container from %s (boot time: %s)", self.image, self.boot_time)

        self.container = docker.run(image=self.image, detach=True, remove=True, publish=[(self.host_port, self.port)])
        self.wait_for_container_running(True)

        time.sleep(self.boot_time)
        logger.debug("Container for %s started...", self.image)

    def stop_container(self):
        logger.info("Stopping container %s of %s ...", self.container, self.image)
        self.container.stop()
        self.container = None
        logger.info("Stopped container %s of %s ...", self.container, self.image)

    def wait_for_container_running(self, expect_running):
        container_state = self.container.state
        while not (expect_running and container_state.running or not expect_running and container_state.dead):
            logger.debug("Waiting for container state %s for %s (current state %s)", "running" if expect_running else "dead", self.image, container_state)
            time.sleep(1)
            container_state = self.container.state