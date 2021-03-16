"""Master for the cluster protocol."""

from socket import socket, gethostname, AF_INET, SOCK_DGRAM, SOCK_STREAM, MSG_DONTWAIT, MSG_PEEK
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
        self.config = config
        self.node_registry = NodeRegistry(config, self)
        self.hostname = gethostname()
        self.slave_sockets = {}

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

    def get_slave_socket(self, address: str) -> None:
        """Returns a TCP socket for the given slave.
        If it doesn't already exist or is no longer open, a new connection will be opened.

        :param str address: IP Address of the slave
        """
        if address not in self.slave_sockets or self.is_socket_closed(self.slave_sockets[address]):
            slave_socket = socket(family=AF_INET, type=SOCK_STREAM)
            slave_socket.connect((address, PORT))
            self.slave_sockets[address] = slave_socket

        return self.slave_sockets[address]

    def is_socket_closed(self, sock: socket) -> bool:  # pylint: disable=no-self-use
        """Checks whether a socket is closed or still open.

        :param socket.socket socket: Socket to check
        """
        try:
            # this will try to read bytes without blocking and also without removing
            # them from buffer (peek only)
            data = sock.recv(16, MSG_DONTWAIT | MSG_PEEK)
            if len(data) == 0:
                return True
        except BlockingIOError:
            # socket is open and reading from it would block
            return False
        except ConnectionResetError:
            # socket was closed for some other reason
            return True
        except Exception as error:  # pylint: disable=broad-except
            print('[Cluster Master] unexpected exception when checking if a socket is closed')
            print(error)
            return False
        return False

    def send_acquisition(self, address: str) -> None:
        """Sends a service acquisition message to a node.

        :param str address: IP Address of the node to acquire
        """
        message = self.build_message()
        message.serviceAcquisition.detect = self.config.balance
        message.serviceAcquisition.hostname = self.hostname

        self.get_slave_socket(address).sendall(message.SerializeToString())

    def send_release(self, address: str) -> None:
        """Sends a service release message to a node.

        :param str address: IP Address of the node to release
        """
        message = self.build_message()
        message.serviceRelease.hostname = self.hostname

        self.get_slave_socket(address).sendall(message.SerializeToString())

    def send_ping(self, address: str) -> None:
        """Sends a ping message to a node.

        :param str address: IP Address of the node
        """
        message = self.build_message()
        message.ping.hostname = self.hostname

        self.get_slave_socket(address).sendall(message.SerializeToString())

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
