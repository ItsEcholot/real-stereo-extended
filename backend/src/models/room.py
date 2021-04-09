"""Implements the state of a single room."""

from typing import List
import models.node
from models.room_calibration_point import RoomCalibrationPoint


class Room:
    """Implements the state of a single room.

    :param int room_id: Room id
    :param str name: Name of the room
    :param List[model.node.Node] nodes: All nodes that are assigned to this room
    """

    def __init__(self, room_id: int = None, name: str = '', nodes: List = None,
                 calibration_points: List = None):
        if len(name) == 0:
            raise ValueError('Room name cannot be empty')

        self.room_id: int = room_id
        self.name: str = name
        self.nodes: List[models.node.Node] = nodes or []
        self.calibrating: bool = False
        self.calibration_points: List[RoomCalibrationPoint] = calibration_points or []
        self.calibration_points_current_point: List[RoomCalibrationPoint] = []
        self.calibration_current_speaker_index = 0
        self.calibration_point_x: int = 0
        self.calibration_point_y: int = 0
        self.calibration_point_freeze: bool = False

    @staticmethod
    def from_json(data: dict):
        """Reads data from a JSON object and returns a new room instance.

        :param dict data: JSON data
        :returns: Room
        :rtype: Room
        """
        return Room(data.get('id'), data.get('name'), data.get('calibration_points'))

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

        return json
