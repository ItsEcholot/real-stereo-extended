"""Room repository."""

from models.room import Room
from .repository import Repository


class RoomRepository(Repository):
    """Room repository.

    :param config.Config config: Config instance
    """

    def __init__(self, config):
        super().__init__()
        self.config = config

    def get_room(self, room_id: int, fail: bool = False) -> Room:
        """Returns the room with the specified id.

        :param int room_id: Room id
        :param bool fail: If true, a ValueError will be raised if the room could not be found
        :returns: Room or None if no room could be found with this id
        :rtype: models.room.Room
        """
        room = next(filter(lambda r: r.room_id == room_id, self.config.rooms), None)

        if fail and room is None:
            raise ValueError('Room with id ' + str(room_id) + ' could not be found')

        return room

    def get_room_by_name(self, name: str) -> Room:
        """Returns the room with the given name.

        :param str name: Room name
        :returns: Room or None if no room could be found with this name
        :rtype: models.room.Room
        """
        return next(filter(lambda r: r.name == name, self.config.rooms), None)

    async def add_room(self, room: Room) -> None:
        """Adds a new room and stores the config file.

        :param models.room.Room room: Room instance
        """
        # assign a new id if the room does not yet have one
        if room.room_id is None:
            rooms_sorted = sorted(self.config.rooms, key=lambda r: r.room_id, reverse=True)
            room.room_id = 1 if rooms_sorted is None or len(
                rooms_sorted) == 0 else rooms_sorted[0].room_id + 1

        self.config.rooms.append(room)
        await self.call_listeners()

    async def remove_room(self, room_id: int) -> bool:
        """Removes a room and stores the config file.

        :param int room_id: Room id
        :returns: False if no room could be found with this id and so no removal was possible,
                  otherwise True.
        :rtype: bool
        """
        room = self.get_room(room_id)

        if room is not None:
            # remove room
            self.config.rooms.remove(room)

            # remove nodes with this room
            nodes_to_remove = list(filter(lambda n: n.room.room_id ==
                                          room.room_id, self.config.nodes))
            for node in nodes_to_remove:
                self.config.nodes.remove(node)

            if len(nodes_to_remove) > 0:
                await self.config.node_repository.call_listeners()

            # remove speakers with this room
            speakers_to_remove = list(filter(lambda s: s.room.room_id ==
                                             room.room_id, self.config.speakers))
            for speaker in speakers_to_remove:
                self.config.speakers.remove(speaker)

            if len(speakers_to_remove) > 0:
                await self.config.speaker_repository.call_listeners()

            await self.call_listeners()

            return True

        return False

    def to_json(self) -> dict:
        """Returns the list of all rooms in JSON serializable objects.

        :returns: JSON serializable object
        :rtype: dict
        """
        return list(map(lambda room: room.to_json(True), self.config.rooms))
