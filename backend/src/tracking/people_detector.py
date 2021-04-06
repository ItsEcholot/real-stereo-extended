"""Defines methods for the people detection."""
from abc import ABC, abstractmethod
from multiprocessing import Queue, Event
from numpy import ndarray
import cv2
from .fps_calculator import Fps


class PeopleDetector(ABC):
    """Defines methods for the people detection."""

    def __init__(self, frame_queue: Queue, frame_result_queue: Queue, return_frame: Event):
        self.frame_queue = frame_queue
        self.frame_result_queue = frame_result_queue
        self.return_frame = return_frame
        self.fps = Fps()

    def process(self) -> None:
        """Starts people detection."""
        while True:
            frame = self.frame_queue.get()
            self.detect(frame, frame)

            # count fps
            self.fps.frame()

            if self.return_frame.is_set():
                # write fps on the image
                cv2.putText(frame, 'FPS: {:.1f}'.format(self.fps.get()), (10, 26),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # send result
                self.frame_result_queue.put_nowait(frame)

    @abstractmethod
    def detect(self, detection_frame: ndarray, draw_frame: ndarray = None) -> None:
        """Detects people in a given camera frame.

        :param numpy.ndarray detection_frame: Camera frame which should be used for detection
        :param numpy.ndarray draw_frame: Frame in which recognized people should be drawn.
                                         If none, result should be drawn in detection_frame.
        """
        raise NotImplementedError()

    def report_coordinate(self, coordinate: int) -> None:
        """Reports the detected coordinate to the master.

        :param int coordinate: Coordinate
        """
        # await self.config.tracking_repository.update_coordinate(coordinate)
