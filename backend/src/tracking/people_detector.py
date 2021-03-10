"""Detects people in a given camera frame."""
import cv2
from numpy import ndarray


class PeopleDetector:
    """Detects people in a given camera frame."""

    def __init__(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def detect(self, frame: ndarray) -> None:
        """Detects people in a given camera frame.

        :param numpy.ndarray frame: Camera frame
        """
        # detect people
        (rects, _) = self.hog.detectMultiScale(frame, winStride=(2, 2), padding=(8, 8), scale=1.05)

        # draw the bounding boxes
        self.draw_rects(frame, rects)

    @staticmethod
    def draw_rects(frame: ndarray, rects: list) -> None:
        """Draws the given rects ontop of the frame.

        :param numpy.ndarray frame: Frame to draw on
        :param list rects: A list of rects in the form (x, y, width, height)
        """
        for (pos_x, pos_y, width, height) in rects:
            cv2.rectangle(frame, (pos_x, pos_y), (pos_x + width, pos_y + height), (0, 255, 0), 2)
