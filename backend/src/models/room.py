"""Implements the state of a single room."""

from typing import List
import models.node
from models.room_calibration_point import RoomCalibrationPoint
from tracking.people_detector import DEFAULT_COORDINATE


class Room:
    """Implements the state of a single room.

    :param int room_id: Room id
    :param str name: Name of the room
    :param List[model.node.Node] nodes: All nodes that are assigned to this room
    :param str people_group: Strategy to calculate the coordinate in case of multiple people
    """

    def __init__(self, room_id: int = None, name: str = '', nodes: List = None,
                 people_group: str = ''):
        if len(name) == 0:
            raise ValueError('Room name cannot be empty')

        self.room_id: int = room_id
        self.name: str = name
        self.nodes: List[models.node.Node] = nodes or []
        self.calibrating: bool = False
        self.calibration_points: List[RoomCalibrationPoint] = []
        self.calibration_points_current_point: List[RoomCalibrationPoint] = []
        self.calibration_current_speaker_index = 0
        self.calibration_point_x: int = 0
        self.calibration_point_y: int = 0
        self.calibration_point_freeze: bool = False
        self.people_group: str = people_group
        self.coordinates: List[int] = [DEFAULT_COORDINATE, DEFAULT_COORDINATE]

    @staticmethod
    def from_json(data: dict):
        """Reads data from a JSON object and returns a new room instance.

        :param dict data: JSON data
        :returns: Room
        :rtype: Room
        """
        return Room(data.get('id'), data.get('name'), people_group=data.get('people_group'))

    def calibration_points_from_json(self, data: dict, config):
        """Reads calibration points from a JSON object and adds it to the current room instance.

        :param dict data: JSON data
        :param config.Config config: Config instance
        """
        if data is not None:
            self.calibration_points = list(map(lambda calibration_point: RoomCalibrationPoint.from_json(calibration_point, config), data))

    def to_json(self, recursive: bool = False) -> dict:
        """Creates a JSON serializable object.

        :param bool recursive: If true, all relations will be returned as full objects as well.
                               If false, only the ids of the relations will be returned.
        :returns: JSON serializable object
        :rtype: dict
        """
        json = {
            'id': self.room_id,
            'name': self.name,
            'calibration_points': list(map(lambda calibration_point: calibration_point.to_json(), self.calibration_points))
        }

        if recursive:
            json['nodes'] = list(map(lambda node: node.to_json(live=True), self.nodes))

        if self.people_group is not None and len(self.people_group) > 0:
            json['people_group'] = self.people_group

        return json
