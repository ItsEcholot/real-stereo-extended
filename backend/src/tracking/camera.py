"""Camera module implements the camera connection and person detection."""

import asyncio
from picamera.array import PiRGBArray  # pylint: disable=import-error
from picamera import PiCamera  # pylint: disable=import-error
import cv2
from numpy import ndarray
from .people_detector import PeopleDetector


class Camera:
    """The Camera class continuously reads frames from the given camera and performs
    feature detection on them.
    """

    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    FRAMERATE: int = 5

    def __init__(self):
        self.exiting = False
        self.detector = PeopleDetector()
        self.on_frame = None
        self.camera = PiCamera()
        self.camera.resolution = (self.FRAME_WIDTH, self.FRAME_HEIGHT)
        self.camera.framerate = self.FRAMERATE

    def stop(self) -> None:
        """Stops reading from the camera after the current frame has been processed."""
        self.exiting = True

    async def process(self) -> None:
        """Processes the camera frames until `stop()` has been called
        or the camera is no longer available."""
        try:
            raw_capture = PiRGBArray(self.camera, size=(self.FRAME_WIDTH, self.FRAME_HEIGHT))
            for frame in self.camera.capture_continuous(raw_capture, format='bgr',
                                                        use_video_port=True):
                frame_data = frame.array
                # self.detector.detect(resized_frame)

                if self.on_frame is not None:
                    self.send_frame(frame_data)

                # clear stream for next frame
                raw_capture.truncate(0)

                if self.exiting:
                    break

                await asyncio.sleep(0.1)
        finally:
            self.camera.close()

        if self.on_frame is not None:
            self.on_frame(None)
            self.on_frame = None

    def send_frame(self, frame: ndarray) -> None:
        """If an `on_frame` callback has been registered, it sends the current frame to it.

        :param numpy.ndarray frame: Current camera frame
        """
        _, jpeg_frame = cv2.imencode('.jpg', frame)
        try:
            self.on_frame(jpeg_frame)
        except TypeError:
            self.on_frame = None
            print('Error occurred in the on_frame callback, it will automatically get unregistered')

    def set_frame_callback(self, on_frame: callable) -> None:
        """Sets the `on_frame` callback that will receive every processed frame.

        :param callable on_frame: Callback that receives the `numpy.ndarray` frame as the first
                                  argument
        """
        self.on_frame = on_frame
