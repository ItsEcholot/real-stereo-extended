"""Implements the state of a single node."""

import models.room


class Node:
    """Implements the state of a single node.

    :param int node_id: Node id
    :param str name: Name of the node
    :param bool online: Whether the node is currently online or not
    :param str ip_address: Local IP adress of the node
    :param str hostname: Hostname of the node
    :param models.room.Room room: Room to which the node belongs to
    :param str detector: Detection algorithm
    """

    def __init__(self, node_id: int = None, name: str = '', online: bool = False,  # pylint: disable=too-many-arguments
                 ip_address: str = '', hostname: str = '', room=None, detector: str = None,
                 coordinate_type: str = ''):
        if len(name) == 0:
            raise ValueError('Node name cannot be empty')

        self.node_id: int = node_id
        self.name: str = name
        self.online: bool = online
        self.ip_address: str = ip_address
        self.hostname: str = hostname
        self.room: models.room.Room = room
        self.detector = detector
        self.coordinate_type = coordinate_type
        self.acquired: bool = False

    def has_coordinate_type(self) -> bool:
        """Returns if the node has a coordinate type set.

        :returns: True if a coordinate type (x or y) is set
        :rtype: bool
        """
        return self.coordinate_type is not None and len(self.coordinate_type) > 0

    @staticmethod
    def from_json(data: dict, config):
        """Reads data from a JSON object and returns a new node instance.

        :param dict data: JSON data
        :param config.Config config: Config instance
        :returns: Node
        :rtype: Node
        """
        # find room in which the node is located
        room = config.room_repository.get_room(data.get('room_id'), fail=True)

        node = Node(node_id=data.get('id'), name=data.get('name'),
                    ip_address=data.get('ip'), hostname=data.get('hostname'), room=room,
                    detector=data.get('detector'), coordinate_type=data.get('coordinate_type'))
        room.nodes.append(node)
        return node

    def to_json(self, recursive: bool = False, live: bool = False) -> dict:
        """Creates a JSON serializable object.

        :param bool recursive: If true, all relations will be returned as full objects as well.
                               If false, only the ids of the relations will be returned.
        :param bool live: If true, live status will be returned.
        :returns: JSON serializable object
        :rtype: dict
        """
        json = {
            'id': self.node_id,
            'name': self.name,
            'ip': self.ip_address,
            'hostname': self.hostname,
        }

        if self.room is not None:
            if recursive:
                json['room'] = self.room.to_json()
            else:
                json['room_id'] = self.room.room_id

        if self.detector is not None and len(self.detector) > 0:
            json['detector'] = self.detector

        if self.coordinate_type is not None and len(self.coordinate_type) > 0:
            json['coordinate_type'] = self.coordinate_type

        if live:
            json['online'] = self.online

        return json
