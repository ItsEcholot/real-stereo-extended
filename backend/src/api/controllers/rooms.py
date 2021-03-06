from socketio import Namespace


class RoomsController(Namespace):
    def __init__(self):
        super().__init__(namespace='/rooms')
        self.rooms = []

    def on_connect(self, sid, environ):
        # send current state to the new client
        self.emit('get', self.rooms, room=sid)

    def on_create(self, sid, data):
        # add the new room and send the new state to all clients
        self.rooms.append(data)
        self.emit('get', self.rooms)
