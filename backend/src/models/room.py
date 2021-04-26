"""Implements the state of a single room."""

from typing import List
import models.node


class Room:
    """Implements the state of a single room.

    :param int room_id: Room id
    :param str name: Name of the room
    :param List[model.node.Node] nodes: All nodes that are assigned to this room
    :param str people_group: Strategy to calculate the coordinate in case of multiple people
    """

    def __init__(self, room_id: int = None, name: str = '', nodes: List = None,
                 people_group: str = ''):
        if len(name) == 0:
            raise ValueError('Room name cannot be empty')

        self.room_id: int = room_id
        self.name: str = name
        self.nodes: List[models.node.Node] = nodes or []
        self.people_group: str = people_group

    @staticmethod
    def from_json(data: dict):
        """Reads data from a JSON object and returns a new room instance.

        :param dict data: JSON data
        :returns: Room
        :rtype: Room
        """
        return Room(data.get('id'), data.get('name'), people_group=data.get('people_group'))

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
            json['nodes'] = list(map(lambda node: node.to_json(live=True), self.nodes))

        if self.people_group is not None and len(self.people_group) > 0:
            json['people_group'] = self.people_group

        return json
