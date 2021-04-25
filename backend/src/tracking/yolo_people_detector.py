"""Detects people in a given camera frame."""
from multiprocessing import Queue, Event
from pathlib import Path
import cv2
from numpy import ndarray, array, argmax
from .people_detector import PeopleDetector


YOLO_PATH: Path = (Path(__file__).resolve().parent / '..' / '..' / 'assets' / 'yolo').resolve()
PERSON_CLASSIFICATION_ID = 0
CONFIDENCE_THRESHOLD = 0.5


class YoloPeopleDetector(PeopleDetector):
    """Detects people in a given camera frame."""

    def __init__(self, frame_queue: Queue, frame_result_queue: Queue, return_frame: Event,
                 coordinate_queue: Queue):
        super().__init__(frame_queue, frame_result_queue, return_frame, coordinate_queue)
        self.name = "YOLO"
        self.net = self.load_net()

    def load_net(self):
        """Loads the yolo net."""
        weights_path = YOLO_PATH / 'tiny3.weights'
        config_path = YOLO_PATH / 'tiny3.cfg'

        return cv2.dnn.readNetFromDarknet(str(config_path), str(weights_path))  # pylint: disable=no-member

    def detect(self, frame: ndarray) -> list:
        """Detects people in a given camera frame.

        :param numpy.ndarray frame: Camera frame which should be used for detection
        :returns: Detected people as bounding boxes
        :rtype: list
        """
        # get target layer names
        layers = self.net.getLayerNames()
        layers = [layers[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        # convert image to a blob and pass it to the net
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),  # pylint: disable=no-member
                                     swapRB=True, crop=False)
        self.net.setInput(blob)

        # process
        results = self.net.forward(layers)

        # convert results to bounding boxes
        rects = self.convert_to_boxes(frame, results)

        return rects

    def convert_to_boxes(self, frame: ndarray, results: list) -> list:
        """Converts the net result to bounding boxes.

        :param numpy.ndarray frame: Frame to draw on
        :param list results: Result list from the net
        """
        height, width = frame.shape[:2]
        boxes = []
        confidences = []

        for result in results:
            for detection in result:
                scores = detection[5:]
                classification = argmax(scores)
                confidence = scores[classification]

                # only continue for people with a high confidence
                if classification == PERSON_CLASSIFICATION_ID and confidence > CONFIDENCE_THRESHOLD:
                    # convert and scale yolo coordinates back to the original ones of the frame
                    (box_x, box_y, box_width, box_height) = detection[0:4] * array([width, height,
                                                                                    width, height])
                    pos_x = box_x - (box_width / 2)
                    pos_y = box_y - (box_height / 2)
                    boxes.append([int(pos_x), int(pos_y), int(box_width), int(box_height)])
                    confidences.append(float(confidence))

        # reduce multiple overlapping bounding boxes to a single one
        final_boxes = []
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.65)  # pylint: disable=no-member

        if len(idxs) > 0:
            for box_id in idxs.flatten():
                final_boxes.append(boxes[box_id])

        return final_boxes
