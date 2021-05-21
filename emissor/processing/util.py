import logging
import time
from python_on_whales import docker

logger = logging.getLogger(__name__)


class DockerInfra:
    def __init__(self, image, port, host_ports, num_jobs, run_on_gpu = False, boot_time=30):
        self.image = image
        self.port = port
        self.host_ports = range(host_ports, host_ports + num_jobs)
        self.num_jobs = num_jobs
        self.run_on_gpu = run_on_gpu
        self.boot_time = boot_time

        self.containers = {}

    def __enter__(self):
        self.start_containers()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_containers()

    def start_containers(self):
        if len(self.containers):
            raise EnvironmentError("Containers already started")

        logger.info("Creating %s containers of %s ...", self.num_jobs, self.image)

        self.containers = []
        for i in range(self.num_jobs):
            container = docker.run(image=self.image, detach=True, remove=True, publish=[(self.host_ports[i], self.port)])
            self.containers.append(container)
            logger.debug("sleeping for %s seconds to warm up %s th container for %s ...", self.boot_time, i, self.image)
            time.sleep(self.boot_time)
            logger.debug("sleeping done for %s th container for %s ...", i, self.image)

    def stop_containers(self):
        for container in self.containers:
            logger.info("stopping the container %s of %s ...", container, self.image)
            container.stop()

        self.containers = []