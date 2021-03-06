from pathlib import Path
from threading import Thread
from queue import Queue
import socketio
import eventlet
from .controllers.rooms import RoomsController

# define path of the static frontend files
frontendPath: str = str(Path(__file__).resolve().parent) + \
    '/../../../frontend/build'


class ApiManager:
    def __init__(self, tracking_manager):
        self.tracking_manager = tracking_manager

        # create the server
        self.server = socketio.Server(cors_allowed_origins='*')
        self.app = socketio.WSGIApp(self.server, wsgi_app=self.handle_request, static_files={
            '/index.html': frontendPath + '/index.html',
            '/static': frontendPath + '/static',
        })
        self.thread = None
        self.stream_queues = []

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
            return self.start_stream(start_response)

        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found']

    def start_api(self):
        print('Listening on http://localhost:8080')
        self.thread = Thread(target=self.listen)
        self.thread.start()

    def listen(self):
        eventlet.wsgi.server(eventlet.listen(
            ('', 8080)), self.app, log_output=False)

    def on_frame(self, frame):
        encapsulated = ('--jpgboundary\r\n' +
                        'Content-Type:image/jpeg\r\n' +
                        'Content-Length:' + str(frame.size) + '\r\n\r\n').encode() + \
            frame.tostring() + '\r\n\r\n'.encode()

        for queue in self.stream_queues:
            queue.put(encapsulated)

    def start_stream(self, start_response):
        start_response('200 OK', [
            ('Content-Type', 'multipart/x-mixed-replace; boundary=--jpgboundary'),
        ])

        if len(self.stream_queues) == 0:
            print('starting camera stream')
            self.tracking_manager.set_frame_callback(self.on_frame)

        requestQueue = Queue()
        self.stream_queues.append(requestQueue)
        while True:
            try:
                yield requestQueue.get()
            except:
                if requestQueue in self.stream_queues:
                    self.stream_queues.remove(requestQueue)
                if len(self.stream_queues) == 0:
                    self.tracking_manager.set_frame_callback(None)
                    print('camera stream stopped')
                return
