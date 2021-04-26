"""Controller for the /rooms namespace."""

from typing import List
from socketio import AsyncNamespace
from config import Config
from models.room import Room
from models.acknowledgment import Acknowledgment
from api.validate import Validate
from protocol.master import ClusterMaster


class RoomsController(AsyncNamespace):
    """Controller for the /rooms namespace."""

    def __init__(self, config: Config, cluster_master: ClusterMaster):
        super().__init__(namespace='/rooms')
        self.config: Config = config
        self.cluster_master: ClusterMaster = cluster_master

        # add room repository change listener
        config.room_repository.register_listener(self.send_rooms)

    async def send_rooms(self, sid: str = None) -> None:
        """Sends the current rooms to all clients or only a specific one.

        :param str sid: If specified, rooms will only be sent to this session id. Otherwise, all
                        clients will receive the rooms.
        """
        await self.emit('get', self.config.room_repository.to_json(), room=sid)

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
        people_group = data.get('people_group')

        validate.string(name, label='Name', min_value=1, max_value=50)

        if people_group is not None:
            validate.string(people_group, label='Handle multiple people', min_value=5, max_value=10)

        if create:
            if self.config.room_repository.get_room_by_name(name) is not None:
                ack.add_error('A room with this name already exists')
        elif validate.integer(room_id, label='Room id', min_value=1):
            existing = self.config.room_repository.get_room_by_name(name)

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
        return self.config.room_repository.to_json()

    async def on_create(self, _: str, data: dict) -> dict:
        """Creates a new room.

        :param str sid: Session id
        :param dict data: Event data
        """
        # validate
        ack = self.validate(data, True)

        # create the new room
        if ack.successful:
            room = Room(name=data.get('name'))

            if data.get('people_group') is not None:
                room.people_group = data.get('people_group')

            # add the new room and send the new state to all clients
            await self.config.room_repository.add_room(room)
            ack.created_id = room.room_id

        return ack.to_json()

    async def on_update(self, _: str, data: dict) -> dict:
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

            if data.get('people_group') is not None:
                room.people_group = data.get('people_group')
                for node in room.nodes:
                    if node.acquired and node.online:
                        self.cluster_master.send_service_update(node.ip_address)

            # store the update and send the new state to all clients
            await self.config.room_repository.call_listeners()

            if len(room.nodes) > 0:
                await self.config.node_repository.call_listeners()

        return ack.to_json()

    async def on_delete(self, _: str, room_id: int) -> dict:
        """Deletes a room.

        :param str sid: Session id
        :param int room_id: Room id
        """
        ack = Acknowledgment()

        if await self.config.room_repository.remove_room(room_id) is False:
            ack.add_error('A room with this id does not exist')

        return ack.to_json()
