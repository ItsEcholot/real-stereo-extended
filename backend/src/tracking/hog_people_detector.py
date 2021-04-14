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
                 coordinate_queue: Queue):
        super().__init__(frame_queue, frame_result_queue, return_frame, coordinate_queue)
        self.name = "HoG"
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def detect(self, frame: ndarray) -> None:
        """Detects people in a given camera frame.

        :param numpy.ndarray frame: Camera frame which should be used for detection
        """
        # detect people
        (rects, _) = self.hog.detectMultiScale(frame, winStride=(3, 3), padding=(8, 8), scale=1.2)

        # reduce multiple overlapping bounding boxes to a single one
        reduced_rects = non_max_suppression(rects, probs=None, overlapThresh=0.1)
        reduced_rects = self.group_nearby_rects(rects, GROUP_THRESHOLD_WIDTH,
                                                GROUP_THRESHOLD_HEIGTH)

        # calculate the coordinate
        if len(reduced_rects) > 0:
            coordinate = self.calculate_coordinate(reduced_rects)
            self.report_coordinate(coordinate)

        # draw the bounding boxes
        self.draw_rects(self.drawing_frame, reduced_rects)
