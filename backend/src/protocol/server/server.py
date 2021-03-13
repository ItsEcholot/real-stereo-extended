"""Server for the cluster protocol."""

from socket import socket, AF_INET, SOCK_DGRAM
from ..socket import ClusterSocket
from ..constants import PORT
from ..cluster_pb2 import Wrapper


class ClusterServer(ClusterSocket):
    """Server for the cluster protocol."""

    def __init__(self):
        super().__init__()
        self.receive_socket = None

    def init(self) -> None:
        """Initializes the server socket and starts listening."""
        self.running = True
        self.receive_socket = socket(family=AF_INET, type=SOCK_DGRAM)
        self.receive_socket.bind(('0.0.0.0', PORT))

        print('Cluster server started on port ' + str(PORT))

        self.run()

    def run(self) -> None:
        """Run logic of the server socket."""
        while self.running:
            self.receive_message(self.receive_socket)

    def on_service_announcement(self, message: Wrapper, address: str) -> None:
        """On service announcement received.

        :param protocol.cluster_pb2.Wrapper wrapper: Message
        :param str address: Sender IP
        """
        print('new service announcement from ' + address + ': ' + str(message))
