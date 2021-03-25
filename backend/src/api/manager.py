"""Handles the web server and incoming requests."""

from pathlib import Path
from typing import List
import asyncio
import socketio
from aiohttp import web, MultipartWriter
from numpy import ndarray
from config import Config, NodeType
from tracking.manager import TrackingManager
from .controllers.rooms import RoomsController
from .controllers.nodes import NodesController
from .controllers.speakers import SpeakersController
from .controllers.settings import SettingsController

# define path of the static frontend files
frontend_path: Path = (Path(__file__).resolve().parent /
                       '..' / '..' / '..' / 'frontend' / 'build').resolve()
assets_path: Path = (Path(__file__).resolve().parent / '..' / '..' / 'assets').resolve()


class ApiManager:
    """The API manager starts a web server and defines the available routes.

    :param Config config: The application config object.
    :param TrackingManager tracking_manager: The instance of an active tracking manager.
    """

    def __init__(self, config: Config, tracking_manager: TrackingManager):
        self.config: Config = config
        self.tracking_manager: TrackingManager = tracking_manager
        self.stream_queues: List[asyncio.Queue] = []
        self.app: web.Application = web.Application()

        # register routes for both masters and slaves
        self.app.add_routes([web.get('/stream.mjpeg', self.get_stream)])

        # register master routes
        if self.config.type == NodeType.MASTER or self.config.type == NodeType.UNCONFIGURED:
            if frontend_path.exists() and (frontend_path / 'static').exists():
                self.app.add_routes([
                    web.get('/{tail:(?!static|socket).*}', self.get_index),
                    web.static('/static', str(frontend_path / 'static')),
                ])

            # attach the socket.io server to the same web server
            self.server = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
            self.server.attach(self.app)

            # register socket.io namespaces
            self.server.register_namespace(RoomsController(config=self.config))
            self.server.register_namespace(NodesController(config=self.config))
            self.server.register_namespace(SpeakersController(config=self.config))
            self.server.register_namespace(SettingsController(config=self.config))

    async def get_index(self, _: web.Request) -> web.Response:
        """Returns the index.html on the / route.

        :param aiohttp.web.Request request: Request instance
        :returns: Response
        :rtype: aiohttp.web.Response
        """
        return web.FileResponse(str(frontend_path / 'index.html'))

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
            print('[Web API] Starting camera stream')
            self.tracking_manager.set_frame_callback(self.on_frame)

        if self.tracking_manager.running is False:
            await self.write_camera_inactive_frame(response)

        queue = asyncio.Queue()
        self.stream_queues.append(queue)

        while True:
            try:
                # write each frame (from the queue)
                frame = await queue.get()

                if frame is None:
                    await self.write_camera_inactive_frame(response)
                else:
                    await self.write_stream_frame(response, frame)

                queue.task_done()
            except:  # pylint: disable=bare-except
                break

        # when the client has closed the connection, remove the queue
        if queue in self.stream_queues:
            # if no other stream request is active, stop catching the camera frames
            if len(self.stream_queues) == 1:
                self.tracking_manager.set_frame_callback(None)
                print('[Web API] Camera stream stopped')
            self.stream_queues.remove(queue)

    async def write_stream_frame(self, response, frame) -> None:
        """Writes a frame to the camera stream.

        :param response: Response
        :param frame: Frame
        """
        with MultipartWriter('image/jpeg', boundary='jpgboundary') as mpwriter:
            mpwriter.append(frame, {
                'Content-Type': 'image/jpeg'
            })
            await mpwriter.write(response, close_boundary=False)
        await response.drain()

    async def write_camera_inactive_frame(self, response) -> None:
        """Writes the camera inactive frame to the stream.

        :param response: Response
        """
        file = open(assets_path / 'camera-inactive.jpg', 'rb')
        image = file.read()
        await self.write_stream_frame(response, image)
        await self.write_stream_frame(response, image)  # send a second time to flush previous

    async def start(self) -> None:
        """Start the API server."""
        print('[Web API] Listening on http://localhost:8080')
        await web._run_app(self.app, host='0.0.0.0', port=8080, handle_signals=False, print=None)  # pylint: disable=protected-access

    def on_frame(self, frame: ndarray) -> None:
        """`on_frame` callback of a `Camera` instance. Will send the frame to all connected clients
        of the stream endpoint.

        :param numpy.ndarray frame: Current camera frame
        """
        # put the frame into all stream request queues so they can be sent in the get_stream method
        for queue in self.stream_queues:
            queue.put_nowait(None if frame is None else frame.tostring())
