"""Slave for the cluster protocol."""

import asyncio
from time import time
from socket import socket, gethostname, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from ..socket import ClusterSocket
from ..constants import PORT, SLAVE_PING_INTERVAL, MASTER_AVAILABILITY_CHECK_INTERVAL
from ..cluster_pb2 import Wrapper


class ClusterSlave(ClusterSocket):
    """Slave for the cluster protocol."""

    def __init__(self, config, tracking):
        super().__init__()
        self.config = config
        self.tracking = tracking
        self.receive_socket = None
        self.send_socket = None
        self.direct_master = None
        self.master_ip = None
        self.last_ping = None

        # register listeners
        self.config.tracking_repository.register_listener(self.on_tracking_repository_changed)

    async def init(self) -> None:
        """Initializes the slave socket and starts listening."""
        self.running = True
        self.send_socket = socket(family=AF_INET, type=SOCK_DGRAM)
        self.send_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.log('Listening on port ' + str(PORT))

        await asyncio.gather(self.update_state(), self.receive())

    async def on_tracking_repository_changed(self) -> None:
        """Updates the coordinate when the tracking repository has been changed."""
        self.send_position_update(self.config.tracking_repository.coordinate)

    def log(self, message: str) -> None:  # pylint: disable=no-self-use
        """Prints a log message to the console.

        :param str message: Log message
        """
        print('[Cluster Slave] ' + message)

    async def update_state(self) -> None:
        """Update state of the slave socket."""
        message = self.build_message()
        message.serviceAnnouncement.hostname = gethostname()

        while self.running:
            # send service announcement if not yet acquired
            if self.master_ip is None:
                self.send_message(message, address='<broadcast>')

            else:
                # check if the master didn't send a ping recently and so is assumed to be offline
                if self.last_ping + MASTER_AVAILABILITY_CHECK_INTERVAL < time():
                    self.log(self.master_ip + ' is offline')
                    await self.on_service_release(None, self.master_ip)

                # send last position update as a ping message if older than 15s
                else:
                    self.send_position_update(self.config.tracking_repository.coordinate)

            await asyncio.sleep(SLAVE_PING_INTERVAL)

    def send_message(self, message: Wrapper, address: str = '') -> None:
        """Sends a message to the master or specified address.

        :param protocol.cluster_pb2.Wrapper message: Message
        :param str address: IP Address of the receiver. If unspecified, master_ip will be used.
        """
        receiver_address = address if len(address) > 0 else self.master_ip

        if self.direct_master is not None:
            asyncio.create_task(self.direct_master.call_events(message, receiver_address))
        else:
            self.send_socket.sendto(message.SerializeToString(), (receiver_address, PORT))

    async def receive(self) -> None:
        """Starts the receiving socket server."""
        await asyncio.start_server(self.handle_client, host='0.0.0.0', port=PORT, family=AF_INET)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) \
            -> None:
        """Receive logic of the slave socket."""
        while self.running and not reader.at_eof():
            try:
                data = await reader.readuntil('\r\n'.encode())
                address = writer.get_extra_info('peername')

                # remove message delimiter
                data = data[:-2]

                await self.receive_message(data, address=address[0])
            except asyncio.IncompleteReadError:
                break
            except RuntimeError as error:
                print(error)

    def send_position_update(self, coordinate: int) -> None:
        """Sends a position update to the master.

        :param int coordinate: Coordinate
        """
        message = self.build_message()
        message.positionUpdate.coordinate = coordinate
        self.send_message(message, self.master_ip)

    def send_camera_calibration_response(self, count: int, image: str) -> None:
        """Sends a camera calibration response to the master.

        :param int count: Count param
        :param str image: Image param
        """
        message = self.build_message()
        message.cameraCalibrationResponse.count = count
        message.cameraCalibrationResponse.image = image
        self.send_message(message, self.master_ip)

    async def on_service_acquisition(self, message: Wrapper, address: str) -> None:
        """Handle service acquisition message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that acquired this service
        """
        self.last_ping = time()
        self.master_ip = address
        self.log('Acquired by ' + address)

        if message.serviceAcquisition.detector is not None and \
                len(message.serviceAcquisition.detector) > 0:
            self.tracking.set_detector(message.serviceAcquisition.detector)

        if message.serviceAcquisition.people_group is not None and \
                len(message.serviceAcquisition.people_group) > 0:
            self.tracking.set_people_group(message.serviceAcquisition.people_group)

        self.config.balance = message.serviceAcquisition.track
        await self.config.setting_repository.call_listeners()

    async def on_service_update(self, message: Wrapper, address: str) -> None:
        """Handle service update message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master
        """
        if address == self.master_ip:
            self.config.balance = message.serviceUpdate.track
            await self.config.setting_repository.call_listeners()

            if message.serviceUpdate.detector is not None and \
                    len(message.serviceUpdate.detector) > 0:
                self.tracking.set_detector(message.serviceUpdate.detector)

            if message.serviceUpdate.people_group is not None and \
                    len(message.serviceUpdate.people_group) > 0:
                self.tracking.set_people_group(message.serviceUpdate.people_group)

    async def on_service_release(self, _: Wrapper, address: str) -> None:
        """Handle service release message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that released this service
        """
        if address == self.master_ip:
            self.master_ip = None
            self.log('Released by ' + address)

            if self.config.balance:
                self.config.balance = False
                await self.config.setting_repository.call_listeners()

    async def on_ping(self, _: Wrapper, address: str) -> None:
        """Handle ping message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that pinged this service
        """
        if address == self.master_ip:
            self.last_ping = time()

    async def on_camera_calibration_request(self, message: Wrapper, address: str) -> None:
        """Handle camera calibration request message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that pinged this service
        """
        if address == self.master_ip:
            start = message.cameraCalibrationRequest.start or False
            finish = message.cameraCalibrationRequest.finish or False
            repeat = message.cameraCalibrationRequest.repeat or False

            self.tracking.send_camera_calibration_request(start, finish, repeat, self)

            if start:
                self.tracking.acquire_camera()
            elif finish:
                self.tracking.release_camera()
