"""Detects people in a given grayscale camera frame."""
from multiprocessing import Queue, Event
import cv2
from numpy import ndarray
from .hog_people_detector import HogPeopleDetector


class HogGrayscalePeopleDetector(HogPeopleDetector):
    """Detects people in a given grayscale camera frame."""

    def __init__(self, frame_queue: Queue, frame_result_queue: Queue, return_frame: Event,
                 coordinate_queue: Queue, people_group: str):
        super().__init__(frame_queue, frame_result_queue, return_frame, coordinate_queue,
                         people_group)
        self.name = "HoG G"

    def detect(self, frame: ndarray) -> list:
        """Detects people in a given camera frame.

        :param numpy.ndarray frame: Camera frame which should be used for detection
        :returns: Detected people as bounding boxes
        :rtype: list
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return super().detect(gray_frame)
