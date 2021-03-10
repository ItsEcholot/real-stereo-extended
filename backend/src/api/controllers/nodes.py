"""Controller for the /nodes namespace."""

from typing import List
import asyncio
from socketio import AsyncNamespace
from config import Config
from models.node import Node
from models.acknowledgment import Acknowledgment
from api.validate import Validate


class NodesController(AsyncNamespace):
    """Controller for the /nodes namespace."""

    def __init__(self, config: Config):
        super().__init__(namespace='/nodes')
        self.config: Config = config

        # add node repository change listener
        config.node_repository.register_listener(self.send_nodes)

    def send_nodes(self, sid: str = None) -> None:
        """Sends the current nodes to all clients or only a specific one.

        :param str sid: If specified, nodes will only be sent to this session id. Otherwise, all
                        clients will receive the nodes.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(
            self.emit('get', self.config.node_repository.to_json(), room=sid))

    def validate(self, data: dict, create: bool) -> Acknowledgment:
        """Validates the input data.

        :param dict data: Input data
        :param bool create: If a new node will be created from this data or an existing updated.
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        node_id = data.get('id')
        name = data.get('name')
        ip_address = data.get('ip')

        validate.string(name, label='Name', min_value=1, max_value=50)
        validate.string(ip_address, label='Ip', min_value=3, max_value=45)

        if data.get('room') is None or isinstance(data.get('room'), dict) is False:
            ack.add_error('Room id must not be empty')
        elif validate.integer(data.get('room').get('id'), label='Room id', min_value=1):
            if self.config.room_repository.get_room(data.get('room').get('id')) is None:
                ack.add_error('A room with this id does not exist')

        if create:
            if self.config.node_repository.get_node_by_name(name) is not None:
                ack.add_error('A node with this name already exists')
            if self.config.node_repository.get_node_by_ip(ip_address) is not None:
                ack.add_error('A node with this ip already exists')
        elif validate.integer(node_id, label='Node id', min_value=1):
            existing_name = self.config.node_repository.get_node_by_name(name)
            existing_ip = self.config.node_repository.get_node_by_ip(
                ip_address)

            if self.config.node_repository.get_node(node_id) is None:
                ack.add_error('Node with this id does not exist')
            elif existing_name and existing_name.node_id != node_id:
                ack.add_error('A node with this name already exists')
            elif existing_ip and existing_ip.node_id != node_id:
                ack.add_error('A node with this ip already exists')

        return ack

    async def on_get(self, _: str) -> List[Node]:
        """Returns the current nodes.

        :param str sid: Session id
        :param dict data: Event data
        """
        return self.config.node_repository.to_json()

    async def on_update(self, _: str, data: dict) -> dict:
        """Updates a node.

        :param str sid: Session id
        :param dict data: Event data
        """
        # validate
        ack = self.validate(data, False)

        # update the node
        if ack.successful:
            room = self.config.room_repository.get_room(
                data.get('room').get('id'))
            node = self.config.node_repository.get_node(data.get('id'))

            node.name = data.get('name')
            node.ip_address = data.get('ip')

            # update room reference if necessary
            if node.room.room_id != room.room_id:
                node.room.nodes.remove(node)
                node.room = room
                node.room.nodes.append(node)

            # store the update and send the new state to all clients
            self.config.node_repository.call_listeners()
            self.config.room_repository.call_listeners()

        return ack.to_json()

    async def on_delete(self, _: str, node_id: int) -> dict:
        """Deletes a node.

        :param str sid: Session id
        :param int node_id: Node id
        """
        ack = Acknowledgment()

        if self.config.node_repository.remove_node(node_id) is False:
            ack.add_error('A node with this id does not exist')

        return ack.to_json()
