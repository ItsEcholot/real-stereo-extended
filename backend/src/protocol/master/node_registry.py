"""Holds information about all available nodes and their state."""
from threading import Thread
from time import time, sleep
import asyncio
from config import Config
from models.node import Node
from ..constants import PINT_INTERVAL, AVAILABILITY_CHECK_INTERVAL
from ..cluster_pb2 import Wrapper


class NodeRegistry:
    """Holds information about all available nodes and their state.

    :param config.Config config: Config instance
    """

    def __init__(self, config: Config):
        self.running = True
        self.config = config
        self.last_pings = {}
        self.check_thread = Thread(target=self.check_availability)
        self.check_thread.start()
        self.ping_thread = Thread(target=self.ping_slaves)
        self.ping_thread.start()

    def stop(self) -> None:
        """Stops the node registry."""
        self.running = False
        self.check_thread.join()
        self.ping_thread.join()

    def log(self, node: Node, message: str) -> None:
        """Prints a log message to the console.

        :param models.node.Node node: Related node
        :param str message: Log message
        """
        print('[Node Registry] ' + node.hostname + ' (' + node.ip_address + ') ' + message)

    def check_availability(self) -> None:
        """Checks if all nodes are still available or marks them offline if not."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        while self.running:
            for node in self.config.nodes:
                # check if the node is still marked as online but didn't send a ping recently
                if node.online and (node.ip_address not in self.last_pings
                                    or self.last_pings[node.ip_address] +
                                    AVAILABILITY_CHECK_INTERVAL < time()):
                    node.online = False
                    self.config.node_repository.call_listeners()
                    self.config.room_repository.call_listeners()
                    self.log(node, 'is offline')

                    # if the node is not assigned to a room, remove it from the list
                    if node.room is None:
                        self.config.node_repository.remove_node(node.node_id)
                        self.log(node, 'removed from registry')

            sleep(AVAILABILITY_CHECK_INTERVAL / 2)

    def ping_slaves(self) -> None:
        """Send a ping message to all slaves."""
        while self.running:
            sleep(PINT_INTERVAL)

    def on_service_announcement(self, message: Wrapper, address: str) -> None:
        """When a service announcment is received, create or update the node in the registry.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP address
        """
        hostname = message.serviceAnnouncement.hostname

        # search by hostname since IPs can change
        node = self.config.node_repository.get_node_by_hostname(hostname)

        # create or update the node
        if node is None:
            node = Node(name=hostname, online=True, ip_address=address, hostname=hostname)
            self.config.node_repository.add_node(node)
            self.log(node, 'added to registry')
        elif node.ip_address != address:
            node.ip_address = address
            self.config.node_repository.call_listeners()
            self.log(node, 'ip address has changed')

        # update node state
        if node.online is False:
            node.online = True
            self.config.node_repository.call_listeners()
            self.config.room_repository.call_listeners()
            self.log(node, 'is online')

        self.last_pings[address] = time()
