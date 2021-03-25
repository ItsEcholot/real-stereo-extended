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
        self.config.setting_repository.register_listener(self.on_settings_changed)

    async def on_settings_changed(self) -> None:
        """Update the tracking status when the settings have changed."""
        if self.config.balance and self.running is False:
            asyncio.create_task(self.start())
        elif self.config.balance is False and self.running:
            self.stop()

    async def start(self) -> None:
        """Start the camera tracking."""
        self.running = True

        print('[Tracking] Starting camera')

        if self.camera is None:
            self.camera = Camera()
            self.camera.on_frame = self.on_frame

        await self.camera.process()

    def stop(self) -> None:
        """Stop the current camera tracking."""
        self.running = False

        if self.camera is not None:
            print('[Tracking] Stopping camera')
            self.camera.stop()
            self.camera.on_frame = None
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
