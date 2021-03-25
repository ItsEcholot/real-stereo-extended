"""Slave for the cluster protocol."""

import asyncio
from time import time
from socket import socket, gethostname, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from ..socket import ClusterSocket
from ..constants import PORT, SLAVE_PING_INTERVAL, MASTER_AVAILABILITY_CHECK_INTERVAL
from ..cluster_pb2 import Wrapper


class ClusterSlave(ClusterSocket):
    """Slave for the cluster protocol."""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.receive_socket = None
        self.send_socket = None
        self.master_ip = None
        self.last_ping = None

    async def init(self) -> None:
        """Initializes the slave socket and starts listening."""
        self.running = True
        self.send_socket = socket(family=AF_INET, type=SOCK_DGRAM)
        self.send_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.log('Listening on port ' + str(PORT))

        await asyncio.gather(self.update_state(), self.receive())

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
                self.send_socket.sendto(message.SerializeToString(), ('<broadcast>', PORT))

            else:
                # check if the master didn't send a ping recently and so is assumed to be offline
                if self.last_ping + MASTER_AVAILABILITY_CHECK_INTERVAL < time():
                    self.log(self.master_ip + ' is offline')
                    await self.on_service_release(None, self.master_ip)

                # send last position update as a ping message if older than 15s
                # else:

            await asyncio.sleep(SLAVE_PING_INTERVAL)

    async def receive(self) -> None:
        """Starts the receiving socket server."""
        await asyncio.start_server(self.handle_client, host='0.0.0.0', port=PORT, family=AF_INET)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) \
            -> None:
        """Receive logic of the slave socket."""
        while self.running and not reader.at_eof():
            try:
                data = await reader.readuntil('\0'.encode())
                address = writer.get_extra_info('peername')

                # remove message delimiter
                data = data[:-1]

                await self.receive_message(data, address=address[0])
            except asyncio.IncompleteReadError:
                break
            except:  # pylint: disable=bare-except
                continue

    async def on_service_acquisition(self, message: Wrapper, address: str) -> None:
        """Handle service acquisition message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that acquired this service
        """
        self.last_ping = time()
        self.master_ip = address
        self.log('Acquired by ' + address)

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

    async def on_service_release(self, _: Wrapper, address: str) -> None:
        """Handle service release message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that released this service
        """
        if address == self.master_ip:
            self.master_ip = None
            self.log('Released by ' + address)

    async def on_ping(self, _: Wrapper, address: str) -> None:
        """Handle ping message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that pinged this service
        """
        if address == self.master_ip:
            self.last_ping = time()
