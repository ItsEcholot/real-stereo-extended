"""Controller for the /rooms namespace."""

from typing import List
import asyncio
from socketio import AsyncNamespace
from config import Config
from models.room import Room
from models.acknowledgment import Acknowledgment
from api.validate import Validate


class RoomsController(AsyncNamespace):
    """Controller for the /rooms namespace."""

    def __init__(self, config: Config):
        super().__init__(namespace='/rooms')
        self.config: Config = config

        # add room repository change listener
        config.room_repository.register_listener(self.send_rooms)

    def send_rooms(self, sid: str = None) -> None:
        """Sends the current rooms to all clients or only a specific one.

        :param str sid: If specified, rooms will only be sent to this session id. Otherwise, all
                        clients will receive the rooms.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.emit('get', list(map(lambda room: room.to_json(True),
                                                   self.config.rooms)), room=sid))

    def validate(self, data: dict, create: bool) -> Acknowledgment:
        """Validates the input data.

        :param dict data: Input data
        :param bool create: If a new room will be created from this data or an existing updated.
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        room_id = data.get('id')
        name = data.get('name')

        validate.string(name, label='Name', min_value=1, max_value=50)

        if create:
            existing = next(filter(lambda r: r.name ==
                                   name, self.config.rooms), None)
            if existing is not None:
                ack.add_error('A room with this name already exists')
        elif validate.integer(room_id, label='Room id', min_value=1):
            existing = next(filter(lambda r: r.name ==
                                   name, self.config.rooms), None)

            if self.config.room_repository.get_room(room_id) is None:
                ack.add_error('Room with this id does not exist')
            elif existing and existing.room_id != room_id:
                ack.add_error('A room with this name already exists')

        return ack

    async def on_get(self, _: str) -> List[Room]:
        """Returns the current rooms.

        :param str sid: Session id
        :param dict data: Event data
        """
        return list(map(lambda room: room.to_json(True), self.config.rooms))

    async def on_create(self, _: str, data: dict) -> None:
        """Creates a new room.

        :param str sid: Session id
        :param dict data: Event data
        """
        # validate
        ack = self.validate(data, True)

        # create the new room
        if ack.successful:
            room = Room(name=data.get('name'))

            # add the new room and send the new state to all clients
            self.config.room_repository.add_room(room)
            ack.created_id = room.room_id

        return ack.to_json()

    async def on_update(self, _: str, data: dict) -> None:
        """Updates a room.

        :param str sid: Session id
        :param dict data: Event data
        """
        # validate
        ack = self.validate(data, False)

        # update the room
        if ack.successful:
            room = self.config.room_repository.get_room(data.get('id'))
            room.name = data.get('name')

            # store the update and send the new state to all clients
            self.config.room_repository.call_listeners()

            if len(room.nodes) > 0:
                self.config.node_repository.call_listeners()

        return ack.to_json()

    async def on_delete(self, _: str, room_id: int) -> None:
        """Deletes a room.

        :param str sid: Session id
        :param int room_id: Room id
        """
        ack = Acknowledgment()

        if self.config.room_repository.remove_room(room_id) is False:
            ack.add_error('A room with this id does not exist')

        return ack.to_json()
