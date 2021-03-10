"""Handles the web server and incoming requests."""

from pathlib import Path
from threading import Thread
from typing import List
import asyncio
import socketio
from janus import Queue
from aiohttp import web, MultipartWriter
from numpy import ndarray
from config import Config, NodeType
from tracking.manager import TrackingManager
from .controllers.rooms import RoomsController
from .controllers.nodes import NodesController

# define path of the static frontend files
frontendPath: Path = (Path(__file__).resolve().parent /
                      '..' / '..' / '..' / 'frontend' / 'build').resolve()


class ApiManager:
    """The API manager starts a web server and defines the available routes.

    :param Config config: The application config object.
    :param TrackingManager tracking_manager: The instance of an active tracking manager.
    """

    def __init__(self, config: Config, tracking_manager: TrackingManager):
        self.config: Config = config
        self.tracking_manager: TrackingManager = tracking_manager
        self.thread: Thread = None
        self.stream_queues: List[Queue] = []
        self.app: web.Application = web.Application()

        # register routes for both masters and slaves
        self.app.add_routes([web.get('/stream.mjpeg', self.get_stream)])

        # register master routes
        if self.config.type == NodeType.MASTER or self.config.type == NodeType.UNCONFIGURED:
            if frontendPath.exists() and (frontendPath / 'static').exists():
                self.app.add_routes([
                    web.get('/', self.get_index),
                    web.static('/static', str(frontendPath / 'static')),
                ])

            # attach the socket.io server to the same web server
            self.server = socketio.AsyncServer(
                cors_allowed_origins='*', async_mode='aiohttp')
            self.server.attach(self.app)

            # register socket.io namespaces
            self.server.register_namespace(RoomsController(config=self.config))
            self.server.register_namespace(NodesController(config=self.config))

    async def get_index(self, _: web.Request) -> web.Response:
        """Returns the index.html on the / route.

        :param aiohttp.web.Request request: Request instance
        :returns: Response
        :rtype: aiohttp.web.Response
        """
        return web.FileResponse(str(frontendPath / 'index.html'))

    async def get_stream(self, request: web.Request) -> web.Response:
        """Starts a new multipart mjpeg stream response of the video camera.
        The stream is available at /stream.mjpeg

        :param aiohttp.web.Request request: Request instance
        :returns: Response
        :rtype: aiohttp.web.Response
        """
        # create a mjpeg stream response
        response = web.StreamResponse(status=200, reason='OK', headers={
            'Content-Type': 'multipart/x-mixed-replace; '
            'boundary=--jpgboundary',
        })
        response.force_close()
        await response.prepare(request)

        # if no other stream request is open, start catching the camera frames
        if len(self.stream_queues) == 0:
            print('starting camera stream')
            self.tracking_manager.set_frame_callback(self.on_frame)

        queue = Queue()
        self.stream_queues.append(queue)

        while True:
            try:
                # write each frame (from the queue)
                frame = await queue.async_q.get()
                with MultipartWriter('image/jpeg', boundary='jpgboundary') as mpwriter:
                    mpwriter.append(frame, {
                        'Content-Type': 'image/jpeg'
                    })
                    await mpwriter.write(response, close_boundary=False)
                queue.async_q.task_done()
            except:  # pylint: disable=bare-except
                break

        # when the client has closed the connection, remove the queue
        if queue in self.stream_queues:
            queue.close()
            # if no other stream request is active, stop catching the camera frames
            if len(self.stream_queues) == 1:
                self.tracking_manager.set_frame_callback(None)
                print('camera stream stopped')
            self.stream_queues.remove(queue)

    def start_api(self) -> None:
        """Start the API server in a separate thread."""
        self.thread = Thread(target=self.listen)
        self.thread.start()

    def listen(self) -> None:
        """Start listening on 0.0.0.0:8080."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        web.run_app(self.app, host='0.0.0.0', port=8080, handle_signals=False)

    def on_frame(self, frame: ndarray) -> None:
        """`on_frame` callback of a `Camera` instance. Will send the frame to all connected clients
        of the stream endpoint.

        :param numpy.ndarray frame: Current camera frame
        """
        # put the frame into all stream request queues so they can be sent in the get_stream method
        for queue in self.stream_queues:
            queue.sync_q.put(frame.tostring())
