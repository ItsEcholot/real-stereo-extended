"""Handles the camera processing."""

import asyncio
from .camera import Camera


class TrackingManager:
    """The tracking manager can start or stop the camera tracking and forward callbacks."""

    def __init__(self, config):
        self.config = config
        self.camera = None
        self.running = False
        self.on_frame = None
        self.on_start = None
        self.config.setting_repository.register_listener(self.on_settings_changed)
        self.previous_config_value = self.config.balance
        self.camera_listeners = 0

    async def on_settings_changed(self) -> None:
        """Update the tracking status when the settings have changed."""
        if self.config.balance and self.config.balance != self.previous_config_value:
            self.acquire_camera()
        elif self.config.balance is False and self.config.balance != self.previous_config_value:
            self.release_camera()

        self.previous_config_value = self.config.balance

    def acquire_camera(self) -> None:
        """Ensures the tracking is running."""
        if self.running is False:
            asyncio.create_task(self.start())
        elif self.on_start is not None:
            self.on_start()  # pylint: disable=not-callable

        self.camera_listeners += 1
        print('[Tracking] Camera acquired ({})'.format(self.camera_listeners))

    def release_camera(self) -> None:
        """Releases the camera and stops it if no other listeners are connected."""
        self.camera_listeners -= 1
        print('[Tracking] Camera released ({})'.format(self.camera_listeners))

        if self.camera_listeners == 0:
            self.stop()

    async def start(self) -> None:
        """Start the camera tracking."""
        self.running = True

        print('[Tracking] Starting camera')

        if self.camera is None:
            self.camera = Camera(self.config)
            self.camera.set_frame_callback(self.on_frame)

        if self.on_start is not None:
            self.on_start()  # pylint: disable=not-callable

        await self.camera.process()

    def stop(self) -> None:
        """Stop the current camera tracking."""
        self.running = False

        if self.camera is not None:
            print('[Tracking] Stopping camera')
            self.camera.stop()
            self.camera = None

    def is_active(self) -> bool:
        """Returns if the tracking is currently running."""
        return self.running

    def set_frame_callback(self, on_frame: callable) -> None:
        """Sets the `on_frame` callback that will receive every processed frame.
        If the tracking is not started, a RuntimeError will be raised.

        :param callable on_frame: Callback that receives the `numpy.ndarray` frame as the first
                                  argument
        """
        self.on_frame = on_frame

        if self.camera is not None:
            self.camera.set_frame_callback(on_frame)
