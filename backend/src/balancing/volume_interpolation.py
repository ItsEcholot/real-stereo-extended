"""Interpolates volume for any specific point in a room."""
from math import sqrt
from models.speaker import Speaker


POWER_PARAM = 1.5


class VolumeInterpolation:
    """Interpolates volume for any specific point in a room."""

    def __init__(self, room):
        self.room = room
        self.target_volume = 0.0
        self.calibration_points = []

    def update(self) -> None:
        """Update the interpolation configuration when the room has changed."""
        self.target_volume = self.calculate_target_volume()
        self.calibration_points = self.preprocess_calibration_points()

    def preprocess_calibration_points(self) -> None:
        """Preprocesses the calibration points."""
        points = {}

        for point in self.room.calibration_points:
            if point.speaker.speaker_id not in points:
                points[point.speaker.speaker_id] = []
            points[point.speaker.speaker_id].append(point)

        return points

    def calculate_target_volume(self) -> float:
        """Calculates the target volume for the room.
        For interpolation, Shepard's method for scattered data is used.

        :returns: Target volume
        :rtype: float
        """
        target_volume = 0.0

        for point in self.room.calibration_points:
            if point.measured_volume > target_volume:
                target_volume = point.measured_volume

        return target_volume

    def calculate_volume(self, coordinate_x: int, coordinate_y: int, speaker: Speaker) -> float:
        """Calculates the volume for the given coordinate and speaker.

        :param int coordinate_x: X coordinate
        :param int coordinate_y: Y coordinate
        :param models.Speaker speaker: Speaker
        """
        if speaker.speaker_id not in self.calibration_points:
            print('Speaker with id {} is not calibrated for room {}'.format(
                speaker.speaker_id, self.room.name))
            return 0.0

        total_weight = 0.0
        total_volume = 0.0

        for point in self.calibration_points[speaker.speaker_id]:
            if point.coordinate_x == coordinate_x and point.coordinate_y == coordinate_y:
                return point.measured_volume

            # calculate distance of configuration point to the coordinate
            distance_x = point.coordinate_x - coordinate_x
            distance_y = point.coordinate_y - coordinate_y

            # calculate weight of the configuration point based on the distance
            weight = 1 / pow(sqrt(distance_x ** 2 + distance_y ** 2), POWER_PARAM)

            # add the weighted volume
            total_volume += weight * point.measured_volume
            total_weight += weight

        return total_volume / total_weight
