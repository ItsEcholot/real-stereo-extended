from socketio import AsyncNamespace


class RoomsController(AsyncNamespace):
    def __init__(self):
        super().__init__(namespace='/rooms')
        self.rooms = []

    async def on_connect(self, sid, _):
        # send current state to the new client
        await self.emit('get', self.rooms, room=sid)

    async def on_create(self, _, data):
        # add the new room and send the new state to all clients
        self.rooms.append(data)
        await self.emit('get', self.rooms)
