"""Master for the cluster protocol."""

from socket import socket, AF_INET, SOCK_DGRAM
import asyncio
from config import Config
from ..socket import ClusterSocket
from ..constants import PORT
from ..cluster_pb2 import Wrapper
from .node_registry import NodeRegistry


class ClusterMaster(ClusterSocket):
    """Master for the cluster protocol."""

    def __init__(self, config: Config):
        super().__init__()
        self.receive_socket = None
        self.node_registry = NodeRegistry(config)

    def init(self) -> None:
        """Initializes the master socket and starts listening."""
        self.running = True
        self.receive_socket = socket(family=AF_INET, type=SOCK_DGRAM)
        self.receive_socket.bind(('0.0.0.0', PORT))

        print('[Cluster Master] Listening on port ' + str(PORT))

        self.run()

    def run(self) -> None:
        """Run logic of the master socket."""
        asyncio.set_event_loop(asyncio.new_event_loop())

        while self.running:
            self.receive_message(self.receive_socket)

    def on_service_announcement(self, message: Wrapper, address: str) -> None:
        """On service announcement received.

        :param protocol.cluster_pb2.Wrapper message: Message
        :param str address: Sender IP
        """
        self.node_registry.on_service_announcement(message, address)

    def on_position_update(self, _: Wrapper, address: str) -> None:
        """Handle position updates. Also, record a received ping.

        :param protocol.cluster_pb2.Wrapper message: Message
        :param str address: Sender IP
        """
        self.node_registry.on_ping(address)
