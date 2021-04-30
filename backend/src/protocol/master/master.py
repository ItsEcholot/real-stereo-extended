"""Master for the cluster protocol."""

from socket import socket, gethostname, AF_INET, SOCK_STREAM, MSG_DONTWAIT, MSG_PEEK
import asyncio
import asyncio_dgram
from config import Config
from ..socket import ClusterSocket
from ..constants import PORT
from ..cluster_pb2 import Wrapper
from .node_registry import NodeRegistry


class ClusterMaster(ClusterSocket):
    """Master for the cluster protocol."""

    def __init__(self, config: Config, direct_slave=None):
        super().__init__()
        self.receive_socket = None
        self.config = config
        self.direct_slave = direct_slave
        self.node_registry = NodeRegistry(config, self)
        self.hostname = gethostname()
        self.slave_sockets = {}
        self.camera_calibration_response_listener = None

        if self.direct_slave is not None:
            self.direct_slave.direct_master = self

    async def init(self) -> None:
        """Initializes the master socket and starts listening."""
        self.running = True
        self.receive_socket = await asyncio_dgram.bind(('0.0.0.0', PORT))

        print('[Cluster Master] Listening on port ' + str(PORT))

        await asyncio.gather(
            self.run(),
            self.node_registry.add_self(),
            self.node_registry.check_availability(),
            self.node_registry.ping_slaves(),
        )

    async def run(self) -> None:
        """Run logic of the master socket."""
        while self.running:
            data, address = await self.receive_socket.recv()
            await self.receive_message(data, address=address[0])

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

    def send_message(self, address: str, message: Wrapper) -> None:
        """Sends a message to the specified address.

        :param str address: IP Address of the receiver
        :param protocol.cluster_pb2.Wrapper message: Message
        """
        try:
            if self.direct_slave is not None and address == self.node_registry.master_ip:
                asyncio.create_task(self.direct_slave.call_events(message, address))
            else:
                self.get_slave_socket(address).sendall(
                    message.SerializeToString() + '\r\n'.encode())
        except ConnectionRefusedError:
            print('[Cluster Master] Unable to send message, connection refused')

    def send_acquisition(self, address: str) -> None:
        """Sends a service acquisition message to a node.

        :param str address: IP Address of the node to acquire
        """
        node = self.config.node_repository.get_node_by_ip(address)
        message = self.build_message()
        message.serviceAcquisition.track = self.config.balance
        message.serviceAcquisition.hostname = self.hostname

        if node.detector is not None and len(node.detector) > 0:
            message.serviceAcquisition.detector = node.detector

        if node.room is not None and node.room.people_group is not None and \
                len(node.room.people_group) > 0:
            message.serviceAcquisition.people_group = node.room.people_group

        self.send_message(address, message)

    def send_release(self, address: str) -> None:
        """Sends a service release message to a node.

        :param str address: IP Address of the node to release
        """
        message = self.build_message()
        message.serviceRelease.hostname = self.hostname
        self.send_message(address, message)

    def send_ping(self, address: str) -> None:
        """Sends a ping message to a node.

        :param str address: IP Address of the node
        """
        message = self.build_message()
        message.ping.hostname = self.hostname
        self.send_message(address, message)

    def send_service_update(self, address: str) -> None:
        """Sends a service update message to a node.

        :param str address: IP Address of the node
        """
        node = self.config.node_repository.get_node_by_ip(address)
        message = self.build_message()
        message.serviceUpdate.track = self.config.balance

        if node.detector is not None and len(node.detector) > 0:
            message.serviceUpdate.detector = node.detector

        if node.room is not None and node.room.people_group is not None and \
                len(node.room.people_group) > 0:
            message.serviceUpdate.people_group = node.room.people_group

        self.send_message(address, message)

    def send_camera_calibration_request(self, address: str, start: bool, finish: bool,
                                        repeat: bool) -> None:
        """Sends a camera calibration request to a node.

        :param str address: IP Address of the node
        :param bool start: If calibration process starts
        :param bool finish: If calibration process finishes
        :param bool repeat: If last step in calibration process is repeated
        """
        message = self.build_message()
        if start is not None:
            message.cameraCalibrationRequest.start = start
        if finish is not None:
            message.cameraCalibrationRequest.finish = finish
        if repeat is not None:
            message.cameraCalibrationRequest.repeat = repeat

        self.send_message(address, message)

    async def on_service_announcement(self, message: Wrapper, address: str) -> None:
        """On service announcement received.

        :param protocol.cluster_pb2.Wrapper message: Message
        :param str address: Sender IP
        """
        await self.node_registry.on_service_announcement(message, address)

    async def on_position_update(self, message: Wrapper, address: str) -> None:
        """Handle position updates. Also, record a received ping.

        :param protocol.cluster_pb2.Wrapper message: Message
        :param str address: Sender IP
        """
        self.node_registry.on_ping(address)

        node = self.config.node_repository.get_node_by_ip(address)
        if node.room is not None and node.has_coordinate_type:
            coordinate_id = 0 if node.coordinate_type == 'x' else 1
            node.room.coordinates[coordinate_id] = message.positionUpdate.coordinate
            print('Coordinate: x={}, y={}'.format(node.room.coordinates[0],
                                                  node.room.coordinates[1]))

    async def on_camera_calibration_response(self, message: Wrapper, address: str) -> None:
        """Handle camera calibration response.

        :param protocol.cluster_pb2.Wrapper message: Message
        :param str address: Sender IP
        """
        node = self.config.node_repository.get_node_by_ip(address)
        count = message.cameraCalibrationResponse.count
        image = message.cameraCalibrationResponse.image

        if self.camera_calibration_response_listener is not None:
            await self.camera_calibration_response_listener(  # pylint: disable=not-callable
                node, count, image)
