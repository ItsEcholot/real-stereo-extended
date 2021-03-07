"""Camera module implements the camera connection and person detection."""

import cv2
from numpy import ndarray


class Camera:
    """The Camera class continuously reads frames from the given camera and performs
    feature detection on them.

    :param int cameraId: Index of the camera to use
    """

    def __init__(self, cameraId: int = 0):
        self.exiting = False
        self.capture = cv2.VideoCapture(cameraId)
        self.on_frame = None

        if self.capture.isOpened() is not True:
            raise RuntimeError('Camera with id ' +
                               str(cameraId) + ' is not available')

    def stop(self) -> None:
        """Stops reading from the camera after the current frame has been processed."""
        self.exiting = True

    def process(self) -> None:
        """Processes the camera frames until `stop()` has been called
        or the camera is no longer available."""
        try:
            while self.exiting is False and self.capture.isOpened() is True:
                _, frame = self.capture.read()

                if self.on_frame is not None:
                    self.send_frame(frame)
        finally:
            self.capture.release()

    def send_frame(self, frame: ndarray) -> None:
        """If an `on_frame` callback has been registered, it sends the current frame to it.

        :param numpy.ndarray frame: Current camera frame
        """
        _, jpeg_frame = cv2.imencode('.jpg', frame)
        try:
            self.on_frame(jpeg_frame)
        except TypeError:
            self.on_frame = None
            print(
                'Error occurred in the on_frame callback, it will automatically get unregistered')

    def set_frame_callback(self, on_frame: callable) -> None:
        """Sets the `on_frame` callback that will receive every processed frame.

        :param callable on_frame: Callback that receives the `numpy.ndarray` frame as the first
                                  argument
        """
        self.on_frame = on_frame
