from time import sleep
import logging
import attr
import docker

@attr.s
class Containerized(object):

    dkr_client = None

    dkr_service = attr.ib(default="service")
    dkr_image = attr.ib(default=None)
    dkr_ports = attr.ib(factory=dict)
    dkr_command = attr.ib(default=None)

    dkr_container = attr.ib(init=False, repr=False)

    def start_servive(self):
        logger = logging.getLogger(self.dkr_service)
        logger.info("Starting up service")

        if not Containerized.dkr_client:
            Containerized.dkr_client = docker.from_env()

        try:
            svc = Containerized.dkr_client.containers.get(self.dkr_service)
        except Exception:
            svc = Containerized.dkr_client.containers.run(image=self.dkr_image,
                                                          name=self.dkr_service,
                                                          command=self.dkr_command,
                                                          ports=self.dkr_ports,
                                                          detach=True,
                                                          remove=True)

        while svc.status != "running":
            svc.reload()
            sleep(1)

        self.dkr_container = svc

    # def __del__(self):
    #     self.stop_service()

    def stop_service(self):
        logger = logging.getLogger(self.dkr_service)
        logger.info("Tearing down service")
        self.dkr_container.stop()
