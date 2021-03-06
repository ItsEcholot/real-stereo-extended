from pathlib import Path
from threading import Thread
import socketio
import eventlet
from .controllers.rooms import RoomsController

# define path of the static frontend files
frontendPath: str = str(Path(__file__).resolve().parent) + \
    '/../../../frontend/build'


class ApiManager:
    def __init__(self):
        # create the server
        self.server = socketio.Server(cors_allowed_origins='*')
        self.app = socketio.WSGIApp(self.server, wsgi_app=self.handle_request, static_files={
            '/index.html': frontendPath + '/index.html',
            '/static': frontendPath + '/static',
        })
        self.thread = None

        # register namespaces
        self.server.register_namespace(RoomsController())

    def handle_request(self, env, start_response):
        path = env['PATH_INFO']

        # redirect / to index.html
        if path == '/':
            start_response('302 Found', [('Location', '/index.html')])
            return []

        # start a camera stream
        if path == '/stream.mjpeg':
            print('stream')
            return []

        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found']

    def startApi(self):
        print('Listening on http://localhost:8080')
        self.thread = Thread(target=self.listen)
        self.thread.start()

    def listen(self):
        eventlet.wsgi.server(eventlet.listen(
            ('', 8080)), self.app, log_output=False)
