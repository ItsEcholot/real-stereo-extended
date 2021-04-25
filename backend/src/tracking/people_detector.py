"""Defines methods for the people detection."""
from abc import ABC, abstractmethod
from multiprocessing import Queue, Event
from queue import Empty
from numpy import ndarray
import cv2
from .fps_calculator import Fps
from .people_tracker import PeopleTracker


GREEN = (0, 120, 0)
ORANGE = (51, 153, 255)
DEFAULT_COORDINATE = 320  # center of the image


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
        self.people = []
        self.fps = Fps()
        self.tracker = PeopleTracker()
        self.last_coordinate = DEFAULT_COORDINATE

    def process(self) -> None:
        """Starts people detection."""
        while True:
            frame = self.frame_queue.get()
            self.drawing_frame = frame
            all_regions = self.detect(frame)

            if len(all_regions) > 0:
                next_people = self.tracker.filter_new_rects(all_regions, self.people)
                self.tracker.rotate_history(all_regions)

                # calculate the coordinate
                if len(next_people) > 0:
                    self.people = next_people
                    coordinate = self.calculate_coordinate(self.people)
                    self.report_coordinate(coordinate)

            # count fps
            self.fps.frame()

            if self.return_frame.is_set():
                # draw rects
                if len(all_regions) > 0:
                    self.draw_rects(self.drawing_frame, all_regions, ORANGE, 1)
                if len(self.people) > 0:
                    self.draw_rects(self.drawing_frame, self.people, GREEN, 2)

                # write fps on the image
                cv2.putText(self.drawing_frame, '{} FPS: {:.1f}'.format(self.name, self.fps.get()),
                            (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # send result
                self.frame_result_queue.put_nowait(self.drawing_frame)

    @abstractmethod
    def detect(self, frame: ndarray) -> list:
        """Detects people in a given camera frame.

        :param numpy.ndarray frame: Camera frame which should be used for detection
        :returns: Detected people as bounding boxes
        :rtype: list
        """
        raise NotImplementedError()

    @staticmethod
    def draw_rects(frame: ndarray, rects: list, color: (int, int, int), thickness: int) -> None:
        """Draws the given rects ontop of the frame.

        :param numpy.ndarray frame: Frame to draw on
        :param list rects: A list of rects in the form (x, y, width, height)
        :param (int, int, int) color: Color of the rectangle
        :param int thickness: Thickness of the rectangle
        """
        for (pos_x, pos_y, width, height) in rects:
            cv2.rectangle(frame, (pos_x, pos_y), (pos_x + width, pos_y + height), color, thickness)

    def calculate_coordinate(self, rects) -> int:
        """Calculates the coordinate of the detected person in the given rects.

        :param array rects: Rects
        """
        if len(rects) < 1:
            return DEFAULT_COORDINATE

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
                if self.tracker.intersects(self.tracker.enlarge_rect(rect, threshold_width,
                                                                     threshold_height),
                                           self.tracker.enlarge_rect(grouped_rect, threshold_width,
                                                                     threshold_height)):
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
