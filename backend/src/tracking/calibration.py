"""Implements camera calibration."""


class Calibration:

    def __init__(self):
        self.calibrating = False
        self.calibration = []
        self.next_calibration = []

    def handle_request(self, start: bool = False, finish: bool = False, repeat: bool = False) \
            -> None:
        if start:
            self.next_calibration = []
        elif repeat and len(self.next_calibration) > 0:
            self.next_calibration.pop()

        if finish:
            self.calibrating = False
            if repeat is False:
                self.calibration = self.next_calibration
        elif self.calibrating is False:
            self.calibrating = True

    def handle_frame(self, frame) -> None:
        pass
