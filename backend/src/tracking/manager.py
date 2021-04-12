"""Handles the camera processing."""

import multiprocessing
import asyncio
from concurrent.futures import ProcessPoolExecutor
import cv2
from .camera import Camera
from .yolo_people_detector import YoloPeopleDetector
from .hog_people_detector import HogPeopleDetector
from .hog_grayscale_people_detector import HogGrayscalePeopleDetector


DEFAULT_DETECTOR = 'yolo'


def start_camera(frame_queue, frame_result_queue, return_frame, detection_active,
                 camera_calibration_requests, camera_calibration_responses) -> None:
    """Starts the camera in a subprocess."""
    camera = Camera(frame_queue, frame_result_queue, return_frame, detection_active,
                    camera_calibration_requests, camera_calibration_responses)
    camera.process()


def start_detector(frame_queue, frame_result_queue, return_frame, coordinate_queue,
                   detector_algorithm) -> None:
    """Starts the people detector in a subprocess."""
    detector = None

    if detector_algorithm is None or detector_algorithm == 'yolo':
        detector = YoloPeopleDetector
    elif detector_algorithm == 'hog':
        detector = HogPeopleDetector
    elif detector_algorithm == 'hog_gray':
        detector = HogGrayscalePeopleDetector
    else:
        raise RuntimeError('Unknown detection algorithm: {}'.format(detector_algorithm))

    instance = detector(frame_queue, frame_result_queue, return_frame, coordinate_queue)
    instance.process()


class TrackingManager:
    """The tracking manager can start or stop the camera tracking and forward callbacks."""

    def __init__(self, config):
        self.config = config
        self.camera_process = None
        self.detector_process = None
        self.detector = DEFAULT_DETECTOR
        self.on_frame = None
        self.config.setting_repository.register_listener(self.on_settings_changed)
        self.previous_config_value = self.config.balance
        self.camera_listeners = 0
        self.cluster_slave = None

        manager = multiprocessing.Manager()
        self.frame_queue = manager.Queue()
        self.frame_result_queue = manager.Queue()
        self.camera_calibration_requests = manager.Queue()
        self.camera_calibration_responses = manager.Queue()
        self.coordinate_queue = manager.Queue()
        self.detection_active = manager.Event()
        self.return_frame = manager.Event()

    async def on_settings_changed(self) -> None:
        """Update the tracking status when the settings have changed."""
        if self.config.balance and self.config.balance != self.previous_config_value:
            self.acquire_camera()
            self.start_detector()
        elif self.config.balance is False and self.config.balance != self.previous_config_value:
            self.release_camera()
            self.stop_detector()

        self.previous_config_value = self.config.balance

    def is_camera_active(self) -> bool:
        """Returns whether the camera is active.

        :returns: True if the camera is active
        :rtype: bool
        """
        return self.camera_process is not None

    def acquire_camera(self) -> None:
        """Ensures the tracking is running."""
        if self.camera_process is None:
            self.start_camera()

        self.camera_listeners += 1
        print('[Tracking] Camera acquired ({})'.format(self.camera_listeners))

    def release_camera(self) -> None:
        """Releases the camera and stops it if no other listeners are connected."""
        self.camera_listeners -= 1
        print('[Tracking] Camera released ({})'.format(self.camera_listeners))

        if self.camera_listeners == 0:
            self.stop_camera()

    def start_camera(self) -> None:
        """Start the camera tracking."""
        if self.camera_process is None:
            print('[Tracking] Starting camera')
            self.camera_process = multiprocessing.Process(
                target=start_camera, args=(self.frame_queue, self.frame_result_queue,
                                           self.return_frame, self.detection_active,
                                           self.camera_calibration_requests,
                                           self.camera_calibration_responses, ))
            self.camera_process.start()

    def start_detector(self) -> None:
        """Start the people detector."""
        if self.detector_process is None:
            print('[Tracking] Starting people detector: {}'.format(self.detector))
            self.detection_active.set()
            self.detector_process = multiprocessing.Process(
                target=start_detector, args=(self.frame_queue, self.frame_result_queue,
                                             self.return_frame, self.coordinate_queue,
                                             self.detector, ))
            self.detector_process.start()

    def stop_camera(self) -> None:
        """Stop the current camera tracking."""
        if self.camera_process is not None:
            print('[Tracking] Stopping camera')
            self.camera_process.kill()
            self.camera_process = None

    def stop_detector(self) -> None:
        """Stop the people detector."""
        if self.detector_process is not None:
            print('[Tracking] Stopping people detector')
            self.detection_active.clear()
            self.detector_process.kill()
            self.detector_process = None

    async def await_frames(self) -> None:
        """Awaits result frames and passes them to the listener."""
        executor = ProcessPoolExecutor(max_workers=1)
        loop = asyncio.get_running_loop()

        while True:
            frame = await loop.run_in_executor(executor, self.frame_result_queue.get)
            if self.on_frame is not None:
                # convert frame to jpeg
                try:
                    if frame is None:
                        self.on_frame(None)
                    else:
                        _, jpeg_frame = cv2.imencode('.jpg', frame)
                        self.on_frame(jpeg_frame)
                except TypeError:
                    self.on_frame = None
                    print('Error occurred in the on_frame callback, it will automatically get '
                          + 'unregistered')

    async def await_coordinates(self) -> None:
        """Awaits coordinates and passes them to the repository."""
        executor = ProcessPoolExecutor(max_workers=1)
        loop = asyncio.get_running_loop()

        while True:
            coordinate = await loop.run_in_executor(executor, self.coordinate_queue.get)
            await self.config.tracking_repository.update_coordinate(coordinate)

    async def await_camera_calibration_responses(self) -> None:
        """Awaits camera calibration responses and passes them to the cluster slave."""
        executor = ProcessPoolExecutor(max_workers=1)
        loop = asyncio.get_running_loop()

        while True:
            count, image = await loop.run_in_executor(executor,
                                                      self.camera_calibration_responses.get)
            if self.cluster_slave is not None:
                self.cluster_slave.send_camera_calibration_response(count, image)

    def set_frame_callback(self, on_frame: callable) -> None:
        """Sets the `on_frame` callback that will receive every processed frame.
        If the tracking is not started, a RuntimeError will be raised.

        :param callable on_frame: Callback that receives the `numpy.ndarray` frame as the first
                                  argument
        """
        self.on_frame = on_frame

        if self.on_frame is not None:
            self.return_frame.set()
        else:
            self.return_frame.clear()

    def send_camera_calibration_request(self, start: bool, finish: bool, repeat: bool,
                                        cluster_slave) -> None:
        """Sends a camera calibration request to the camera process.

        :param bool start: If true, a new calibration will be started
        :param bool finish: If true, the current calibration will be finished
        :param bool repeat: If true, the current step will be repeated
        """
        self.cluster_slave = cluster_slave
        self.camera_calibration_requests.put_nowait((start, finish, repeat))

    def set_detector(self, detector: str) -> None:
        """Sets the detection algorithm.

        :param str detector: New detection algorithm
        """
        if self.detector != detector:
            self.detector = detector

            if self.detector_process is not None:
                self.stop_detector()
                self.start_detector()
