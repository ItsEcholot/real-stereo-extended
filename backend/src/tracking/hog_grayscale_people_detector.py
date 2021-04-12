"""Detects people in a given grayscale camera frame."""
from multiprocessing import Queue, Event
import cv2
from numpy import ndarray
from .hog_people_detector import HogPeopleDetector


class HogGrayscalePeopleDetector(HogPeopleDetector):
    """Detects people in a given grayscale camera frame."""

    def __init__(self, frame_queue: Queue, frame_result_queue: Queue, return_frame: Event,
                 coordinate_queue: Queue):
        super().__init__(frame_queue, frame_result_queue, return_frame, coordinate_queue)
        self.name = "HoG G"

    def detect(self, detection_frame: ndarray, draw_frame: ndarray = None) -> None:
        """Detects people in a given camera frame.

        :param numpy.ndarray detection_frame: Camera frame which should be used for detection
        :param numpy.ndarray draw_frame: Frame in which recognized people should be drawn.
                                         If none, result should be drawn in detection_frame.
        """
        gray_frame = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2GRAY)
        return super().detect(gray_frame, detection_frame)
