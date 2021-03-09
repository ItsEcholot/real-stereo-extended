"""Config module implements loading, parsing and storing of the config file."""

import json
from pathlib import Path
from typing import List
from models.room import Room
from models.node import Node
from models.speaker import Speaker
from .node_type import NodeType


class Config:
    """The Config class loads and parses the application config.
    It holds all information and can write them back to the config file again.

    :param Path path: Path of the config.json file
    """

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
            'nodes': list(map(lambda node: node.to_json(), self.nodes)),
            'speakers': list(map(lambda speaker: speaker.to_json(), self.speakers)),
        }

        with open(str(self.path), 'w') as file:
            json.dump(data, file, indent=4)

    def get_room(self, room_id: int, fail: bool = False) -> Room:
        """Returns the room with the specified id.

        :param int room_id: Room id
        :param bool fail: If true, a ValueError will be raised if the room could not be found
        :returns: Room or None if no room could be found with this id
        :rtype: models.room.Room
        """
        room = next(filter(lambda r: r.room_id == room_id, self.rooms), None)

        if fail and room is None:
            raise ValueError('Room with id ' + str(room_id) +
                             ' could not be found')

        return room

    def add_room(self, room: Room) -> None:
        """Adds a new room and stores the config file.

        :param models.room.Room room: Room instance
        """
        # assign a new id if the room does not yet have one
        if room.room_id is None:
            rooms_sorted = sorted(
                self.rooms, key=lambda r: r.room_id, reverse=True)
            room.room_id = 1 if rooms_sorted is None or len(
                rooms_sorted) == 0 else rooms_sorted[0].room_id + 1

        self.rooms.append(room)
        self.store()

    def remove_room(self, room_id: int) -> bool:
        """Removes a room and stores the config file.

        :param int room_id: Room id
        :returns: False if no room could be found with this id and so no removal was possible,
                  otherwise True.
        :rtype: bool
        """
        room = self.get_room(room_id)

        if room is not None:
            # remove room
            self.rooms.remove(room)

            # remove nodes with this room
            nodes_to_remove = map(lambda n: n.room_id ==
                                  room.room_id, self.nodes)
            for node in nodes_to_remove:
                self.nodes.remove(node)

            # remove speakers with this room
            speakers_to_remove = map(
                lambda s: s.room_id == room.room_id, self.speakers)
            for speaker in speakers_to_remove:
                self.speakers.remove(speaker)

            self.store()

            return True

        return False