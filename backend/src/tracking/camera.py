"""Camera module implements the camera connection and person detection."""

from time import sleep
from multiprocessing import Queue, Event
from queue import Empty
from picamera.array import PiRGBArray  # pylint: disable=import-error
from picamera import PiCamera  # pylint: disable=import-error
import cv2
from .calibration import Calibration


class Camera:
    """The Camera class continuously reads frames from the given camera and performs
    feature detection on them.
    """

    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    FRAMERATE: int = 5

    def __init__(self, frame_queue: Queue, frame_result_queue: Queue, return_frame: Event,
                 detection_active: Event, calibration_requests: Queue,
                 calibration_responses: Queue):
        self.frame_queue = frame_queue
        self.frame_result_queue = frame_result_queue
        self.return_frame = return_frame
        self.detection_active = detection_active
        self.calibration_requests = calibration_requests
        self.calibration_responses = calibration_responses
        self.on_frame = None
        self.calibration = Calibration((self.FRAME_WIDTH, self.FRAME_HEIGHT), calibration_responses)
        self.camera = PiCamera()
        self.camera.resolution = (self.FRAME_WIDTH, self.FRAME_HEIGHT)
        self.camera.framerate = self.FRAMERATE

    def process(self) -> None:
        """Processes the camera frames until `stop()` has been called
        or the camera is no longer available."""
        try:
            raw_capture = PiRGBArray(self.camera, size=(self.FRAME_WIDTH, self.FRAME_HEIGHT))
            for frame in self.camera.capture_continuous(raw_capture, format='bgr',
                                                        use_video_port=True):
                frame_data = frame.array

                # process calibration requests
                while not self.calibration_requests.empty():
                    try:
                        start, finish, repeat = self.calibration_requests.get_nowait()
                        self.calibration.handle_request(start, finish, repeat)
                    except Empty:
                        pass

                if self.calibration.calibrating:
                    self.calibration.handle_frame(frame_data)
                    cv2.putText(frame_data, 'Calibrating Camera', (10, self.FRAME_HEIGHT - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    frame_data = self.calibration.correct_frame(frame_data)

                    # clear current frame queue
                    while not self.frame_queue.empty():
                        try:
                            self.frame_queue.get_nowait()
                        except Empty:
                            pass

                    # add frame to the queue
                    self.frame_queue.put_nowait(frame_data)

                if self.return_frame.is_set() and not self.detection_active.is_set():
                    # call frame listener
                    self.frame_result_queue.put_nowait(frame_data)

                # clear stream for next frame
                raw_capture.truncate(0)

                sleep(0.1)
        finally:
            self.camera.close()

        if self.return_frame.is_set():
            self.frame_result_queue.put_nowait(None)
