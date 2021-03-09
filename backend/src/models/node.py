import models.room


class Node:
    def __init__(self, node_id: int = None, name: str = '', online: bool = False,  # pylint: disable=too-many-arguments
                 ip_address: str = '', hostname: str = '', room=None):
        if len(name) == 0:
            raise ValueError('Node name cannot be empty')

        self.node_id: int = node_id
        self.name: str = name
        self.online: bool = online
        self.ip_address: str = ip_address
        self.hostname: str = hostname
        self.room: models.room.Room = room

    def to_json(self, recursive: bool = False) -> dict:
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

        return json
