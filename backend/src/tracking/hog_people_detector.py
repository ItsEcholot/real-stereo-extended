"""Detects people in a given camera frame."""
from multiprocessing import Queue, Event
import cv2
from numpy import ndarray
from imutils.object_detection import non_max_suppression
from .people_detector import PeopleDetector


class HogPeopleDetector(PeopleDetector):
    """Detects people in a given camera frame."""

    def __init__(self, frame_queue: Queue, frame_result_queue: Queue, return_frame: Event):
        super().__init__(frame_queue, frame_result_queue, return_frame)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def detect(self, detection_frame: ndarray, draw_frame: ndarray = None) -> None:
        """Detects people in a given camera frame.

        :param numpy.ndarray detection_frame: Camera frame which should be used for detection
        :param numpy.ndarray draw_frame: Frame in which recognized people should be drawn.
                                         If none, result should be drawn in detection_frame.
        """
        # detect people
        (rects, _) = self.hog.detectMultiScale(detection_frame, winStride=(3, 3), padding=(8, 8),
                                               scale=1.2)

        # reduce multiple overlapping bounding boxes to a single one
        reduced_rects = non_max_suppression(rects, probs=None, overlapThresh=0.65)

        # calculate the coordinate
        if len(reduced_rects) > 0:
            coordinate = self.calculate_coordinate(reduced_rects)
            self.report_coordinate(coordinate)

        # draw the bounding boxes
        self.draw_rects(draw_frame if draw_frame is not None else detection_frame, reduced_rects)

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
