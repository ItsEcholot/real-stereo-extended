"""Controller for the /rooms namespace."""

from socketio import AsyncNamespace


class RoomsController(AsyncNamespace):
    """Controller for the /rooms namespace."""

    def __init__(self):
        super().__init__(namespace='/rooms')
        self.rooms = []

    async def on_connect(self, sid: str, _: dict) -> None:
        """Handles connection of a new client.

        :param str sid: Session id
        :param dict env: Connection information
        """
        # send current state to the new client
        await self.emit('get', self.rooms, room=sid)

    async def on_create(self, _: str, data: dict) -> None:
        """Creates a new room.

        :param str sid: Session id
        :param dict data: Event data
        """
        # add the new room and send the new state to all clients
        self.rooms.append(data)
        await self.emit('get', self.rooms)
