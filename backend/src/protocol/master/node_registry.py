"""Holds information about all available nodes and their state."""
from time import time
from socket import gethostname, gethostbyname
import asyncio
from config import Config
from models.node import Node
from ..constants import MASTER_PING_INTERVAL, NODE_AVAILABILITY_CHECK_INTERVAL
from ..cluster_pb2 import Wrapper


class NodeRegistry:
    """Holds information about all available nodes and their state.

    :param config.Config config: Config instance
    :param protocol.master.ClusterMaster master: Cluster master instance
    """

    def __init__(self, config: Config, master):
        self.running = True
        self.config = config
        self.master = master
        self.last_pings = {}
        self.master_ip = ''

        # add repository change listeners
        config.node_repository.register_listener(self.update_acquisition_status)
        config.setting_repository.register_listener(self.update_service_status)

    def stop(self) -> None:
        """Stops the node registry."""
        self.running = False

    def log(self, node: Node, message: str) -> None:  # pylint: disable=no-self-use
        """Prints a log message to the console.

        :param models.node.Node node: Related node
        :param str message: Log message
        """
        print('[Node Registry] ' + node.hostname + ' (' + node.ip_address + ') ' + message)

    async def update_acquisition_status(self) -> None:
        """Checks if the acquisition state for all nodes is correct
        or acquire/release them if necessary.
        """
        for node in self.config.nodes:
            # acquire if necessary
            if node.room is not None and node.acquired is False and node.online:
                if node.ip_address != self.master_ip:
                    self.master.send_acquisition(node.ip_address)
                elif self.master.direct_slave is not None:
                    if node.detector is not None:
                        self.master.direct_slave.tracking.set_detector(node.detector)
                    if node.room is not None and node.room.people_group is not None and \
                            len(node.room.people_group) > 0:
                        self.master.direct_slave.tracking.set_people_group(node.room.people_group)

                node.acquired = True
                self.log(node, 'acquired')

            # release if necessary
            elif node.room is None and node.acquired and node.online:
                if node.ip_address != self.master_ip:
                    self.master.send_release(node.ip_address)

                node.acquired = False
                self.log(node, 'released')

    async def update_service_status(self) -> None:
        """Updates the service status of all slaves."""
        for node in self.config.nodes:
            if node.acquired and node.online and node.ip_address != self.master_ip:
                self.master.send_service_update(node.ip_address)

    async def check_availability(self) -> None:
        """Checks if all nodes are still available or marks them offline if not."""

        while self.running:
            for node in self.config.nodes:
                # check if the node is still marked as online but didn't send a ping recently
                if node.online and node.ip_address != self.master_ip \
                    and (node.ip_address not in self.last_pings
                         or self.last_pings[node.ip_address] +
                         NODE_AVAILABILITY_CHECK_INTERVAL < time()):
                    node.online = False
                    node.acquired = False
                    await self.config.node_repository.call_listeners()
                    await self.config.room_repository.call_listeners()
                    self.log(node, 'is offline')

                    # if the node is not assigned to a room, remove it from the list
                    if node.room is None:
                        await self.config.node_repository.remove_node(node.node_id)
                        self.log(node, 'removed from registry')

            await asyncio.sleep(NODE_AVAILABILITY_CHECK_INTERVAL / 2)

    async def ping_slaves(self) -> None:
        """Send a ping message to all slaves."""
        while self.running:
            for node in self.config.nodes:
                if node.online and node.ip_address != self.master_ip and node.acquired:
                    self.master.send_ping(node.ip_address)

            await asyncio.sleep(MASTER_PING_INTERVAL)

    async def add_self(self) -> None:
        """Adds the master as a node since it also runs a camera node instance."""
        hostname = gethostname()

        try:
            self.master_ip = gethostbyname(hostname)
        except:  # pylint: disable=bare-except
            self.master_ip = '127.0.0.1'

        if self.master.direct_slave is not None:
            self.master.direct_slave.master_ip = self.master_ip

        await self.update_node(hostname, self.master_ip)

    async def on_service_announcement(self, message: Wrapper, address: str) -> None:
        """When a service announcment is received, create or update the node in the registry.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP address
        """
        hostname = message.serviceAnnouncement.hostname

        # update node
        await self.update_node(hostname, address)
        self.last_pings[address] = time()

    async def update_node(self, hostname: str, ip_address: str) -> None:
        """Updates the given node or creates a new one if it does not yet exist.

        :param str hostname: Hostname of the node
        :param str ip_address: IP Address of the node
        """
        # search by hostname since IPs can change
        node = self.config.node_repository.get_node_by_hostname(hostname)

        # create or update the node
        if node is None:
            node = Node(name=hostname, online=True, ip_address=ip_address, hostname=hostname)
            await self.config.node_repository.add_node(node)
            self.log(node, 'added to registry')
        elif node.ip_address != ip_address:
            node.ip_address = ip_address
            await self.config.node_repository.call_listeners()
            self.log(node, 'ip address has changed')

        # update node state
        if node.online is False:
            node.online = True
            self.log(node, 'is online')
            await self.config.node_repository.call_listeners()
            await self.config.room_repository.call_listeners()

        # acquire node if necessary
        if node.room is not None and node.acquired is False:
            if node.ip_address != self.master_ip:
                self.master.send_acquisition(node.ip_address)

            node.acquired = True
            self.log(node, 'acquired')

    def on_ping(self, address: str) -> None:
        """Records a new ping received from the given ip address.

        :param str address: Sender IP address
        """
        self.last_pings[address] = time()
