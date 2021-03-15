"""Slave for the cluster protocol."""

from threading import Thread
from time import sleep, time
from socket import socket, gethostname, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_BROADCAST
from ..socket import ClusterSocket
from ..constants import PORT, SLAVE_PING_INTERVAL, MASTER_AVAILABILITY_CHECK_INTERVAL
from ..cluster_pb2 import Wrapper


class ClusterSlave(ClusterSocket):
    """Slave for the cluster protocol."""

    def __init__(self):
        super().__init__()
        self.receive_socket = None
        self.send_socket = None
        self.update_thread = None
        self.master_ip = None
        self.last_ping = None

    def init(self) -> None:
        """Initializes the slave socket and starts listening."""
        self.running = True
        self.receive_socket = socket(family=AF_INET, type=SOCK_STREAM)
        self.receive_socket.bind(('0.0.0.0', PORT))
        self.send_socket = socket(family=AF_INET, type=SOCK_DGRAM)
        self.send_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.log('Listening on port ' + str(PORT))

        self.update_thread = Thread(target=self.update_state)
        self.update_thread.start()

        self.receive()

    def stop(self) -> None:
        """Stops the socket."""
        super().stop()
        self.update_thread.join()

    def log(self, message: str) -> None:  # pylint: disable=no-self-use
        """Prints a log message to the console.

        :param str message: Log message
        """
        print('[Cluster Slave] ' + message)

    def update_state(self) -> None:
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
                    self.on_service_release(None, self.master_ip)

                # send last position update as a ping message if older than 15s
                # else:

            sleep(SLAVE_PING_INTERVAL)

    def receive(self) -> None:
        """Receive logic of the slave socket."""
        self.receive_socket.listen()

        while self.running:
            connection, address = self.receive_socket.accept()
            with connection:
                while self.running:
                    message, _ = self.receive_message(connection, address=address[0])
                    if message is None:
                        break

    def on_service_acquisition(self, _: Wrapper, address: str) -> None:
        """Handle service acquisition message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that acquired this service
        """
        self.last_ping = time()
        self.master_ip = address
        self.log('Acquired by ' + address)

    def on_service_release(self, _: Wrapper, address: str) -> None:
        """Handle service release message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that released this service
        """
        if address == self.master_ip:
            self.master_ip = None
            self.log('Released by ' + address)

    def on_ping(self, _: Wrapper, address: str) -> None:
        """Handle ping message.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP Address of the master that pinged this service
        """
        if address == self.master_ip:
            self.last_ping = time()
