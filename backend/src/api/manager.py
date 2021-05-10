"""Handles the web server and incoming requests."""

from pathlib import Path
from typing import List
import asyncio
import ssl
import socketio
from aiohttp import web, MultipartWriter, ClientSession
from numpy import ndarray
from config import Config, NodeType
from tracking.manager import TrackingManager
from protocol.master import ClusterMaster
from balancing.manager import BalancingManager
from .controllers.rooms import RoomsController
from .controllers.nodes import NodesController
from .controllers.speakers import SpeakersController
from .controllers.settings import SettingsController
from .controllers.camera_calibration import CameraCalibrationController
from .controllers.room_calibration import RoomCalibrationController
from .controllers.balances import BalancesController
from .controllers.networks import NetworksController
from .ssl_generator import SSLGenerator

# define path of the static frontend files
frontend_path: Path = (Path(__file__).resolve().parent /
                       '..' / '..' / '..' / 'frontend' / 'build').resolve()
assets_path: Path = (Path(__file__).resolve().parent / '..' / '..' / 'assets').resolve()


class ApiManager:
    """The API manager starts a web server and defines the available routes.

    :param Config config: The application config object.
    :param TrackingManager tracking_manager: The instance of an active tracking manager.
    :param ClusterMaster cluster_master: The cluster master instance if the current node is a master
    """

    def __init__(self, config: Config, tracking_manager: TrackingManager,
                 cluster_master: ClusterMaster = None,
                 balancing_manager: BalancingManager = None):
        self.config: Config = config
        self.tracking_manager: TrackingManager = tracking_manager
        self.stream_queues: List[asyncio.Queue] = []
        self.app: web.Application = web.Application()

        # register routes for both masters and slaves
        self.app.add_routes([
            web.get('/stream.mjpeg', self.get_stream),
            web.get('/backend-assets/calibration/{image}/proxy', self.get_proxy_assets),
            web.static('/backend-assets', str(assets_path)),
        ])

        # register master routes
        if self.config.type == NodeType.MASTER or self.config.type == NodeType.UNCONFIGURED:
            if frontend_path.exists() and (frontend_path / 'static').exists():
                self.app.add_routes([
                    web.get('/{tail:(?!static|socket).*}', self.get_index),
                    web.static('/static', str(frontend_path / 'static')),
                ])

            # add an insecure http web application used for sonos sound assets
            self.insecure_app: web.Application = web.Application()
            self.insecure_app.add_routes([
                web.static('/backend-assets', str(assets_path)),
            ])

            # attach the socket.io server to the same web server
            self.server = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
            self.server.attach(self.app)

            # register socket.io namespaces
            self.server.register_namespace(RoomsController(config=self.config,
                                                           cluster_master=cluster_master))
            self.server.register_namespace(NodesController(config=self.config,
                                                           cluster_master=cluster_master))
            self.server.register_namespace(SpeakersController(config=self.config))
            self.server.register_namespace(SettingsController(config=self.config))
            self.server.register_namespace(CameraCalibrationController(config=self.config,
                                                                       cluster_master=cluster_master))
            self.server.register_namespace(RoomCalibrationController(config=self.config,
                                                                     sonos=getattr(
                                                                         balancing_manager, 'sonos', None),
                                                                     tracking_manager=tracking_manager,
                                                                     cluster_master=cluster_master))
            self.server.register_namespace(NetworksController())
            balances_controller = BalancesController()
            if balancing_manager is not None:
                balancing_manager.balances_api_controller = balances_controller
            self.server.register_namespace(balances_controller)

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

        # proxy if query contains node id
        if 'nodeId' in request.rel_url.query:
            node_id = int(request.rel_url.query['nodeId'])
            node = self.config.node_repository.get_node(node_id)
            async with ClientSession() as client:
                async with client.request(method='get', url='https://{}:8080/stream.mjpeg'.format(node.ip_address), ssl=False) as res:
                    async for data in res.content.iter_any():
                        await response.write(data)
                        if data:
                            await response.drain()
            return response

        # if no other stream request is open, start catching the camera frames
        if len(self.stream_queues) == 0:
            print('[Web API] Starting camera stream')
            self.tracking_manager.set_frame_callback(self.on_frame)

        if self.tracking_manager.is_camera_active() is False:
            await self.write_camera_inactive_frame(response)

        self.tracking_manager.acquire_camera()

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

        self.tracking_manager.release_camera()

        # when the client has closed the connection, remove the queue
        if queue in self.stream_queues:
            # if no other stream request is active, stop catching the camera frames
            if len(self.stream_queues) == 1:
                self.tracking_manager.set_frame_callback(None)
                print('[Web API] Camera stream stopped')
            self.stream_queues.remove(queue)

    async def get_proxy_assets(self, request: web.Request) -> web.Response:
        image = request.match_info['image']
        node_id = int(request.rel_url.query['nodeId'])
        node = self.config.node_repository.get_node(node_id)

        async with ClientSession() as client:
            async with client.request(method='get', url='https://{}:8080/backend-assets/calibration/{}'.format(node.ip_address, image), ssl=False) as res:
                proxied_response = web.Response(headers=res.headers, status=res.status)
                await proxied_response.prepare(request)
                async for data in res.content.iter_any():
                    await proxied_response.write(data)
                    if data:
                        await proxied_response.drain()
        return proxied_response

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
        file = open(frontend_path / '..' / 'src' / 'assets' / 'camera-inactive.jpg', 'rb')
        image = file.read()
        await self.write_stream_frame(response, image)
        await self.write_stream_frame(response, image)  # send a second time to flush previous

    async def start(self) -> None:
        """Start the API server."""
        ssl_generator = SSLGenerator()
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(ssl_generator.certificate_path,
                                    ssl_generator.certificate_path_key)
        print('[Web API] Listening on https://localhost:8080')
        self.ignore_aiohttp_ssl_eror(asyncio.get_event_loop())
        apps = [web._run_app(self.app, host='0.0.0.0', port=8080, handle_signals=False,  # pylint: disable=protected-access
                             print=None, ssl_context=ssl_context)]
        if self.config.type == NodeType.MASTER:
            print('[Web API INSECURE] Listening on http://localhost:8079 (for Sonos media assets)')
            apps.append(web._run_app(self.insecure_app, host='0.0.0.0', port=8079,  # pylint: disable=protected-access
                                     handle_signals=False, print=None))
        await asyncio.gather(*apps)

    def on_frame(self, frame: ndarray) -> None:
        """`on_frame` callback of a `Camera` instance. Will send the frame to all connected clients
        of the stream endpoint.

        :param numpy.ndarray frame: Current camera frame
        """
        # put the frame into all stream request queues so they can be sent in the get_stream method
        for queue in self.stream_queues:
            queue.put_nowait(None if frame is None else frame.tostring())

    def ignore_aiohttp_ssl_eror(self, loop):
        """Ignore aiohttp ssl errors that occur when the site is loaded in chrome (desktop/android).

        :param asyncio.Loop loop: Loop in which aiohttp is running
        """
        original_handler = loop.get_exception_handler()
        messages = ['SSL error in data received', 'SSL handshake failed']

        def ignore_ssl_error(loop, context):
            if context.get('message') in messages:
                exception = context.get('exception')
                if isinstance(exception, ssl.SSLError):
                    if exception.reason == 'SSLV3_ALERT_CERTIFICATE_UNKNOWN' or \
                            exception.reason == 'KRB5_S_INIT':
                        return

            if original_handler is not None:
                original_handler(loop, context)
            else:
                loop.default_exception_handler(context)

        loop.set_exception_handler(ignore_ssl_error)
