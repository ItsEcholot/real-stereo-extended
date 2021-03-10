"""Implements the state of a single room."""

from typing import List
import models.node


class Room:
    """Implements the state of a single room.

    :param int room_id: Room id
    :param str name: Name of the room
    :param List[model.node.Node] nodes: All nodes that are assigned to this room
    """

    def __init__(self, room_id: int = None, name: str = '', nodes: List = None):
        if len(name) == 0:
            raise ValueError('Room name cannot be empty')

        self.room_id: int = room_id
        self.name: str = name
        self.nodes: List[models.node.Node] = nodes or []

    @staticmethod
    def from_json(data: dict):
        """Reads data from a JSON object and returns a new room instance.

        :param dict data: JSON data
        :returns: Room
        :rtype: Room
        """
        return Room(data.get('id'), data.get('name'))

    def to_json(self, recursive: bool = False) -> dict:
        """Creates a JSON serializable object.

        :param bool recursive: If true, all relations will be returned as full objects as well.
                               If false, only the ids of the relations will be returned.
        :returns: JSON serializable object
        :rtype: dict
        """
        json = {
            'id': self.room_id,
            'name': self.name,
        }

        if recursive:
            json['nodes'] = list(
                map(lambda node: node.to_json(live=True), self.nodes))

        return json
