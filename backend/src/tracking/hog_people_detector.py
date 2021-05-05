"""Detects people in a given camera frame."""
from multiprocessing import Queue, Event
import cv2
from numpy import ndarray
from imutils.object_detection import non_max_suppression
from .people_detector import PeopleDetector


GROUP_THRESHOLD_WIDTH = 50
GROUP_THRESHOLD_HEIGTH = 50


class HogPeopleDetector(PeopleDetector):
    """Detects people in a given camera frame."""

    def __init__(self, frame_queue: Queue, frame_result_queue: Queue, return_frame: Event,
                 coordinate_queue: Queue, people_group: str):
        super().__init__(frame_queue, frame_result_queue, return_frame, coordinate_queue,
                         people_group)
        self.name = "HoG"
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.tracker.group_threshold_width = GROUP_THRESHOLD_WIDTH
        self.tracker.group_threshold_height = GROUP_THRESHOLD_HEIGTH

    def detect(self, frame: ndarray) -> list:
        """Detects people in a given camera frame.

        :param numpy.ndarray frame: Camera frame which should be used for detection
        :returns: Detected people as bounding boxes
        :rtype: list
        """
        # detect people
        (rects, _) = self.hog.detectMultiScale(frame, winStride=(3, 3), padding=(8, 8), scale=1.2)

        # reduce multiple overlapping bounding boxes to a single one
        reduced_rects = non_max_suppression(rects, probs=None, overlapThresh=0.01)
        reduced_rects = self.group_nearby_rects(rects, GROUP_THRESHOLD_WIDTH,
                                                GROUP_THRESHOLD_HEIGTH)

        return reduced_rects
