"""Interpolates volume for any specific point in a room."""
from math import sqrt
from models.speaker import Speaker


POWER_PARAM = 1.5


class VolumeInterpolation:
    """Interpolates volume for any specific point in a room."""

    def __init__(self, room):
        self.room = room
        self.target_volume = 0.0
        self.calibration_points = {}
        self.speakers = []

    def update(self) -> None:
        """Update the interpolation configuration when the room has changed."""
        self.target_volume = self.calculate_target_volume()
        self.preprocess_calibration_points()

    def preprocess_calibration_points(self) -> None:
        """Preprocesses the calibration points."""
        self.calibration_points = {}
        self.speakers = []

        for point in self.room.calibration_points:
            if point.speaker.speaker_id not in self.calibration_points:
                self.calibration_points[point.speaker.speaker_id] = []
                self.speakers.append(point.speaker)
            self.calibration_points[point.speaker.speaker_id].append(point)

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

    def calculate_perceived_volume(self, speaker: Speaker) -> float:
        """Calculates the perceived volume for the given coordinate and speaker.

        :param models.Speaker speaker: Speaker
        :returns: Perceived volume
        :rtype: float
        """
        if speaker.speaker_id not in self.calibration_points:
            print('Speaker with id {} is not calibrated for room {}'.format(
                speaker.speaker_id, self.room.name))
            return 0.0

        coordinate_x = self.room.coordinates[0]
        coordinate_y = self.room.coordinates[1]

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

    def calculate_speaker_volume(self, perceived_volume: float) -> int:
        """Calculates the volume that should be set for the speaker and the perceived volume.

        :param float perceived_volume: Perceived volume
        :returns: Speaker volume
        :rtype: float
        """
        # difference from the perceived volume to the target volume
        # if they are the same, it results in 1
        # if the perceived volume is lower, it results in >1 (meaning speaker should be louder)
        # if the perceived volume is higher, it results in <1 (meaning speaker should be quieter)
        percentage_difference = 2 - 1 / self.target_volume * perceived_volume
        corrected_speaker_volume = round(self.room.user_volume * percentage_difference)

        return corrected_speaker_volume
