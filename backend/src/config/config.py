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
            room = next(r for r in self.rooms if r.room_id ==
                        node_data['room_id'])

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
            room = next(r for r in self.rooms if r.room_id ==
                        speaker_data['room_id'])

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
            json.dump(data, file)
