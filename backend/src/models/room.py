from typing import List
import models.node


class Room:
    def __init__(self, room_id: int = None, name: str = '', nodes: List = None):
        if len(name) == 0:
            raise ValueError('Room name cannot be empty')

        self.room_id: int = room_id
        self.name: str = name
        self.nodes: List[models.node.Node] = nodes or []

    def to_json(self, recursive: bool = False) -> dict:
        json = {
            'id': self.room_id,
            'name': self.name,
        }

        if recursive:
            json['nodes'] = list(map(lambda node: node.to_json(), self.nodes))

        return json
