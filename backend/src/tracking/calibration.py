"""Implements camera calibration."""
from time import time
from pathlib import Path
import shutil
import cv2
import numpy as np

CHESSBOARD_SIZE = (7, 7)  #  inner size
PREPARATION_TIME = 3
CORNER_WINDOW_SIZE = (11, 11)
CORNER_ZERO_ZONE = (-1, -1)
CORNER_CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
IMAGE_PATH: Path = (Path(__file__).resolve().parent / '..' / '..' / 'assets' / 'calibration') \
    .resolve()


class Calibration:
    """Implements camera calibration."""

    def __init__(self):
        self.calibrating = False
        self.calibration = []
        self.next_chessboard_at = None
        self.object_points = []
        self.image_points = []
        self.cluster_slave = None

    def handle_request(self, start: bool = False, finish: bool = False, repeat: bool = False) \
            -> None:
        """Handle a camera calibration request.

        :param bool start: If true, a new calibration will be started
        :param bool finish: If true, the current calibration will be finished
        :param bool repeat: If true, the current step will be repeated
        """
        if start:
            print('[Camera Calibration] Starting calibration')

            # 3d points in real world
            self.object_points = []

            # 2d points on the image
            self.image_points = []
        elif repeat and len(self.object_points) > 0:
            self.object_points.pop()
            self.image_points.pop()

        if finish:
            print('[Camera Calibration] Finishing calibration')
            self.calibrating = False

            # cleanup files
            shutil.rmtree(IMAGE_PATH)
        elif self.calibrating is False:
            self.calibrating = True

        if not finish:
            self.next_chessboard_at = time() + PREPARATION_TIME

    def handle_frame(self, frame) -> None:
        """Handle a camera frame by searching for the chessboard.

        :param array frame: Camera frame
        """
        if self.next_chessboard_at is None or self.next_chessboard_at > time():
            return True

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray_frame, CHESSBOARD_SIZE, None)

        # process if chessboard was found
        if ret is True:
            print('[Camera Calibration] Chessboard found')
            self.next_chessboard_at = None

            # improve corner detection
            improved_corners = cv2.cornerSubPix(gray_frame, corners, CORNER_WINDOW_SIZE,
                                                CORNER_ZERO_ZONE, CORNER_CRITERIA)
            self.add_points(improved_corners)

            file_name = self.save_chessboard_image(frame, improved_corners)

            # call master
            if self.cluster_slave is not None:
                self.cluster_slave.send_camera_calibration_response(len(self.object_points),
                                                                    file_name)

    def add_points(self, image_points) -> None:
        """Add the found chessboard points to the results.

        :param array image_points: Points of the chessboard within the 2d image
        """
        # 3d point in real world (1 piece = 1)
        object_points = np.zeros((CHESSBOARD_SIZE[1] * CHESSBOARD_SIZE[0], 3), np.float32)
        object_points[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)
        self.object_points.append(object_points)

        # 2d point on the image
        self.image_points.append(image_points)

    def save_chessboard_image(self, frame, corners) -> str:
        """Saves the image including the found chessboard to a file.

        :param array frame: Camera frame
        :param array corners: Found corners
        :returns: Filename of the image
        :rtype: str
        """
        # draw chessboard on image
        chessboard_image = cv2.drawChessboardCorners(frame, CHESSBOARD_SIZE, corners, True)

        # save file
        file_name = str(int(time())) + '.jpg'
        IMAGE_PATH.mkdir(exist_ok=True)
        print(str(IMAGE_PATH))
        print(str(IMAGE_PATH / file_name))
        cv2.imwrite(str(IMAGE_PATH / file_name), chessboard_image)

        return file_name
