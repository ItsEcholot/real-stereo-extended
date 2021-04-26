"""Detects people in a given camera frame."""
from multiprocessing import Queue, Event
import cv2
from numpy import ndarray, array
from imutils.object_detection import non_max_suppression
from .people_detector import PeopleDetector


GAUSSIAN_BLUR = 15
THRESHOLD = 25
MIN_CONTOUR_SIZE = 500
GROUP_THRESHOLD_WIDTH = 100
GROUP_THRESHOLD_HEIGTH = 500


class MotionPeopleDetector(PeopleDetector):
    """Detects people in a given camera frame."""

    def __init__(self, frame_queue: Queue, frame_result_queue: Queue, return_frame: Event,
                 coordinate_queue: Queue, people_group: str):
        super().__init__(frame_queue, frame_result_queue, return_frame, coordinate_queue,
                         people_group)
        self.name = "Motion"
        self.last_frame = None
        self.tracker.group_threshold_width = GROUP_THRESHOLD_WIDTH
        self.tracker.group_threshold_height = GROUP_THRESHOLD_HEIGTH

    def detect(self, frame: ndarray) -> list:
        """Detects people in a given camera frame.

        :param numpy.ndarray frame: Camera frame which should be used for detection
        :returns: Detected people as bounding boxes
        :rtype: list
        """
        # convert to grayscale and smooth frame
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (GAUSSIAN_BLUR, GAUSSIAN_BLUR), 0)

        # requires last frame to already exist
        if self.last_frame is None:
            self.last_frame = gray_frame
            return []

        # difference to last frame
        diff = cv2.absdiff(self.last_frame, gray_frame)
        self.last_frame = gray_frame

        # apply threshold
        _, diff = cv2.threshold(diff, THRESHOLD, 255, cv2.THRESH_BINARY)

        # find contours in image
        contours, _ = cv2.findContours(diff, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # filter contours and convert them to bounding rects
        rects = []
        for contour in contours:
            if cv2.contourArea(contour) < MIN_CONTOUR_SIZE:
                continue

            rect = cv2.boundingRect(contour)
            rects.append(rect)

        # reduce multiple overlapping and nearby bounding boxes to a single one
        reduced_rects = non_max_suppression(array(rects), probs=None, overlapThresh=0)
        reduced_rects = self.group_nearby_rects(reduced_rects, GROUP_THRESHOLD_WIDTH,
                                                GROUP_THRESHOLD_HEIGTH)

        return reduced_rects
