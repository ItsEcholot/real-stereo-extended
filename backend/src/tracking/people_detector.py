"""Defines methods for the people detection."""
from abc import ABC, abstractmethod
from multiprocessing import Queue, Event
from queue import Empty
from numpy import ndarray
import cv2
from .fps_calculator import Fps


class PeopleDetector(ABC):
    """Defines methods for the people detection."""

    def __init__(self, frame_queue: Queue, frame_result_queue: Queue, return_frame: Event,
                 coordinate_queue: Queue):
        self.name = "Unset"
        self.frame_queue = frame_queue
        self.frame_result_queue = frame_result_queue
        self.return_frame = return_frame
        self.coordinate_queue = coordinate_queue
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
                cv2.putText(frame, '{} FPS: {:.1f}'.format(self.name, self.fps.get()), (10, 26),
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

    @staticmethod
    def draw_rects(frame: ndarray, rects: list) -> None:
        """Draws the given rects ontop of the frame.

        :param numpy.ndarray frame: Frame to draw on
        :param list rects: A list of rects in the form (x, y, width, height)
        """
        for (pos_x, pos_y, width, height) in rects:
            cv2.rectangle(frame, (pos_x, pos_y), (pos_x + width, pos_y + height), (0, 255, 0), 2)

    def calculate_coordinate(self, rects) -> int:
        """Calculates the coordinate of the detected person in the given rects.

        :param array rects: Rects
        """
        if len(rects) < 1:
            return 0

        # take the average x coordinate over all rects
        total = 0.0
        for (x_coordinate, _, width, _) in rects:
            total += x_coordinate + (width / 2.0)

        return int(total / len(rects))

    def report_coordinate(self, coordinate: int) -> None:
        """Reports the detected coordinate to the master.

        :param int coordinate: Coordinate
        """
        # clear current queue
        while not self.coordinate_queue.empty():
            try:
                self.coordinate_queue.get_nowait()
            except Empty:
                pass

        # add new coordinate to the queue
        self.coordinate_queue.put_nowait(coordinate)
