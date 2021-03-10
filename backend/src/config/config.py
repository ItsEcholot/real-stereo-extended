"""Config module implements loading, parsing and storing of the config file."""

import json
from pathlib import Path
from typing import List
from models.room import Room
from models.node import Node
from models.speaker import Speaker
from repositories.room import RoomRepository
from repositories.node import NodeRepository
from repositories.speaker import SpeakerRepository
from repositories.settings import SettingsRepository
from .node_type import NodeType


class Config:
    """The Config class loads and parses the application config.
    It holds all information and can write them back to the config file again.

    :param Path path: Path of the config.json file
    """

    def __init__(self, path: Path = Path('./config.json')):
        self.path: Path = path
        self.type: NodeType = NodeType.UNCONFIGURED
        self.balance: bool = False
        self.rooms: List[Room] = []
        self.nodes: List[Node] = []
        self.speakers: List[Speaker] = []
        self.room_repository = RoomRepository(self)
        self.node_repository = NodeRepository(self)
        self.speaker_repository = SpeakerRepository(self)
        self.setting_repository = SettingsRepository(self)

        # register repository change listeners
        self.room_repository.register_listener(self.store)
        self.node_repository.register_listener(self.store)
        self.speaker_repository.register_listener(self.store)

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
        """Loads the configuration file and parses it into class attributes."""
        self.type = NodeType[self.data.get('type').upper()]

        # load rooms
        for room_data in self.data.get('rooms'):
            self.rooms.append(Room.from_json(room_data))

        # load nodes
        for node_data in self.data.get('nodes'):
            self.nodes.append(Node.from_json(node_data, self))

        # load speakers
        for speaker_data in self.data.get('speakers'):
            self.speakers.append(Speaker.from_json(speaker_data, self))

    def store(self) -> None:
        """Stores the current configuration values back in the config file."""
        data = {
            'type': str(self.type).lower().split('.')[1],
            'rooms': list(map(lambda room: room.to_json(), self.rooms)),
            'nodes': list(map(lambda node: node.to_json(),
                              list(filter(lambda node: node.room is not None, self.nodes)))),
            'speakers': list(map(lambda speaker: speaker.to_json(),
                                 list(filter(lambda speaker: speaker.room is not None,
                                             self.speakers)))),
        }

        with open(str(self.path), 'w') as file:
            json.dump(data, file, indent=4)
