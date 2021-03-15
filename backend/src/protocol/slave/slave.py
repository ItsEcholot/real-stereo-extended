"""Slave for the cluster protocol."""

from time import sleep
from socket import socket, gethostname, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from ..socket import ClusterSocket
from ..constants import PORT


class ClusterSlave(ClusterSocket):
    """Slave for the cluster protocol."""

    def __init__(self):
        super().__init__()
        self.send_socket = None

    def init(self) -> None:
        """Initializes the slave socket and starts listening."""
        self.running = True
        self.send_socket = socket(family=AF_INET, type=SOCK_DGRAM)
        self.send_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        print('[Cluster Slave] Listening on port ' + str(PORT))

        self.run()

    def run(self) -> None:
        """Run logic of the slave socket."""
        message = self.build_message()
        message.serviceAnnouncement.hostname = gethostname()

        while self.running:
            self.send_socket.sendto(message.SerializeToString(), ('<broadcast>', PORT))
            sleep(15)
