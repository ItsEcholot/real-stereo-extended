import json
from pathlib import Path
from typing import List
from .node_type import NodeType
from models.room import Room
from models.node import Node
from models.speaker import Speaker


class Config:
    def __init__(self, path: Path = Path('./config.json')):
        self.path: Path = path
        self.type: NodeType = NodeType.UNCONFIGURED
        self.rooms: List[Room] = []
        self.nodes: List[Node] = []
        self.speakers: List[Speaker] = []

        # load file if it exists
        if path.exists():
            with open(str(path), 'r') as file:
                self.data = json.load(file)
                self.load()

        # otherwise, create the file from a default configuration
        else:
            print('Config ' + str(path) +
                  ' does not exist, creating default configuration')
            self.store()

    def load(self) -> None:
        self.type = NodeType[self.data['type'].upper()]

        # load rooms
        for room_data in self.data['rooms']:
            room = Room(room_id=room_data['id'], name=room_data['name'])
            self.rooms.append(room)

        # load nodes
        for node_data in self.data['nodes']:
            # find room in which the node is located
            room = self.get_room(node_data['room_id'])

            if room is None:
                raise ValueError(
                    'Room with id ' + str(node_data['room_id']) + ' could not be found')

            node = Node(node_id=node_data['id'], name=node_data['name'],
                        ip_address=node_data['ip'], hostname=node_data['hostname'], room=room)
            room.nodes.append(node)
            self.nodes.append(node)

        # load speakers
        for speaker_data in self.data['speakers']:
            # find room in which the speaker is located
            room = self.get_room(speaker_data['room_id'])

            if room is None:
                raise ValueError(
                    'Room with id ' + str(speaker_data['room_id']) + ' could not be found')

            speaker = Speaker(
                speaker_id=speaker_data['id'], name=speaker_data['name'], room=room)
            self.speakers.append(speaker)

    def store(self) -> None:
        data = {
            'type': str(self.type).lower().split('.')[1],
            'rooms': list(map(lambda room: room.to_json(), self.rooms)),
            'nodes': list(map(lambda node: node.to_json(), self.nodes)),
            'speakers': list(map(lambda speaker: speaker.to_json(), self.speakers)),
        }

        with open(str(self.path), 'w') as file:
            json.dump(data, file, indent=4)

    def get_room(self, room_id: int) -> Room:
        room = next(filter(lambda r: r.room_id == room_id, self.rooms), None)
        return room

    def add_room(self, room: Room) -> None:
        # assign a new id if the room does not yet have one
        if room.room_id is None:
            rooms_sorted = sorted(
                self.rooms, key=lambda r: r.room_id, reverse=True)
            room.room_id = 1 if rooms_sorted is None or len(
                rooms_sorted) == 0 else rooms_sorted[0].room_id + 1

        self.rooms.append(room)
        self.store()

    def remove_room(self, room_id: int) -> bool:
        room = self.get_room(room_id)

        if room is not None:
            # todo: also remove all nodes & speakers that were assigned to this room
            self.rooms.remove(room)
            self.store()

            return True

        return False
