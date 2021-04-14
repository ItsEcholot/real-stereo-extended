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
        self.drawing_frame = None
        self.fps = Fps()

    def process(self) -> None:
        """Starts people detection."""
        while True:
            frame = self.frame_queue.get()
            self.drawing_frame = frame
            self.detect(frame)

            # count fps
            self.fps.frame()

            if self.return_frame.is_set():
                # write fps on the image
                cv2.putText(self.drawing_frame, '{} FPS: {:.1f}'.format(self.name, self.fps.get()),
                            (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # send result
                self.frame_result_queue.put_nowait(self.drawing_frame)

    @abstractmethod
    def detect(self, frame: ndarray) -> None:
        """Detects people in a given camera frame.

        :param numpy.ndarray frame: Camera frame which should be used for detection
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

    def group_nearby_rects(self, rects: list, threshold_width: int, threshold_height: int) -> list:
        """Groups nearby rectangles into a greater one.

        :param array rects: Rectangles
        :param int threshold_width: Width threshold
        :param int threshold_height: Height threshold
        :returns: Grouped rectangles
        :rtype: list
        """
        grouped = []

        for rect in rects:
            (pos_x, pos_y, width, height) = rect
            intersects = False
            for grouped_rect in grouped:
                if self.intersects(self.enlarge_rect(rect, threshold_width, threshold_height),
                                   self.enlarge_rect(grouped_rect, threshold_width, threshold_height)):
                    intersects = True

                    # update existing rect
                    max_right = max(grouped_rect[0] + grouped_rect[2], pos_x + width)
                    max_bottom = max(grouped_rect[1] + grouped_rect[3], pos_y + height)
                    grouped_rect[0] = min(grouped_rect[0], pos_x)
                    grouped_rect[1] = min(grouped_rect[1], pos_y)
                    grouped_rect[2] = max_right - pos_x
                    grouped_rect[3] = max_bottom - pos_y

            if not intersects:
                grouped.append(rect)

        return grouped

    def enlarge_rect(self, rect: (int, int, int, int), pixels_width: int, pixels_height: int) \
            -> (int, int, int, int):
        """Enlarges a rectangle by the given amount of pixels.

        :param (int, int, int, int) rect: Rectangle
        :param int pixels_width: Width
        :param int pixels_height: Height
        :returns: Enlarged rectangle
        :rtype: (int, int, int, int)
        """
        return (rect[0] - pixels_width / 2, rect[1] - pixels_height / 2,
                rect[2] + pixels_width, rect[3] + pixels_height)

    def intersects(self, rect1: (int, int, int, int), rect2: (int, int, int, int)) -> bool:
        """Checks if two rectangles are intersecting each other.

        :param (int, int, int, int) rect1: Rectangle
        :param (int, int, int, int) rect2: Rectangle
        :returns: True if they are intersecting
        :rtype: bool
        """
        (x_1, y_1, w_1, h_1) = rect1
        (x_2, y_2, w_2, h_2) = rect2
        if x_1 + w_1 < x_2 or x_2 + w_2 < x_1 or y_1 + h_1 < y_2 or y_2 + h_2 < y_1:
            return False
        return True
