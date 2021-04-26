"""Tracks people across multiple camera frames to eliminate outliers and false-positives."""


class PeopleTracker:
    """Tracks people across multiple camera frames to eliminate outliers and false-positives."""

    def __init__(self, history_size: int = 2, group_threshold_width: int = 50,
                 group_threshold_height: int = 50):
        self.history_size = history_size
        self.group_threshold_width = group_threshold_width
        self.group_threshold_height = group_threshold_height
        self.history = []

    def filter_new_rects(self, rects: list, confirmed_people: list) -> list:
        """Filters out new rectangles based on the previous history to eliminate false-positives.

        :param list rects: Detected bounding boxes
        :param list confirmed_people: Confirmed people from the last frame
        :returns: Only bounding boxes that are already present in the history
        :rtype: list
        """
        # return last people if no more were detected
        if len(rects) == 0:
            return confirmed_people

        # return all if first frame
        if len(confirmed_people) == 0 or len(self.history) == 0:
            return rects

        result = []

        for rect in rects:
            enlarged_rect = self.enlarge_rect(rect, self.group_threshold_width,
                                              self.group_threshold_height)

            # check if overlaps with previous frame
            for prev_rect in confirmed_people:
                if self.intersects(enlarged_rect, prev_rect):
                    result.append(rect)
                    break
            # check if at the same position in the whole history
            else:
                rects_to_check = [enlarged_rect]
                for history in self.history:
                    next_history_rects = []
                    for prev_rect in history:
                        for rect_to_check in rects_to_check:
                            if self.intersects(rect_to_check, prev_rect):
                                next_history_rects.append(self.enlarge_rect(prev_rect,
                                                                            self.group_threshold_width,
                                                                            self.group_threshold_height))
                    if len(next_history_rects) == 0:
                        break
                    rects_to_check = next_history_rects
                else:
                    result.append(rect)

        return result

    def rotate_history(self, rects: list) -> None:
        """Add new confirmed people to the history and ensure it does not exceed the defined length.

        :param list rects: Detected bounding boxes
        """
        self.history.append(rects)

        if len(self.history) > self.history_size:
            self.history.pop(0)

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
