from pathlib import Path
import socketio
import eventlet
from api.controllers.rooms import RoomsController

# define path of the static frontend files
frontendPath: str = str(Path(__file__).resolve().parent) + \
    '/../../../frontend/build'


# create the server
server = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(server, static_files={
    '/': frontendPath + '/index.html',
    '/static': frontendPath + '/static',
})


# register namespaces
server.register_namespace(RoomsController())


# start the web server in a separate thread
def startApi():
    print('Listening on http://localhost:8080')
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app, log_output=False)
