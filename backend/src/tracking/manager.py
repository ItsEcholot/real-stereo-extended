"""Handles the camera processing."""

from .camera import Camera


class TrackingManager:
    """The tracking manager can start or stop the camera tracking and forward callbacks."""

    def __init__(self):
        self.camera = None

    async def start(self) -> None:
        """Start the camera tracking."""
        self.camera = Camera(1)
        await self.camera.process()

    def stop(self) -> None:
        """Stop the current camera tracking."""
        if self.camera is not None:
            self.camera.stop()

    def set_frame_callback(self, on_frame: callable) -> None:
        """Sets the `on_frame` callback that will receive every processed frame.
        If the tracking is not started, a RuntimeError will be raised.

        :param callable on_frame: Callback that receives the `numpy.ndarray` frame as the first
                                  argument
        """
        if self.camera is None:
            raise RuntimeError('Tracking is not available')

        self.camera.set_frame_callback(on_frame)
