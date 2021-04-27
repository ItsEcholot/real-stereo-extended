"""Containes a single calibration point for a room"""

from models.speaker import Speaker

class RoomCalibrationPoint:
    """Containes a single calibration point for a room and a speaker
    
    :param models.speaker.Speaker speaker: Speaker which was playing the test sound
    :param int coordinate_x: The x coordinate of the calibration point
    :param int coordinate_y: The y coordinate of the calibration point
    :param float measured_volume: The measured volume of the sample
    """
    def __init__(self, speaker: Speaker, coordinate_x: int, coordinate_y: int, 
                 measured_volume: float):
        self.speaker: Speaker = speaker
        self.coordinate_x: int = coordinate_x
        self.coordinate_y: int = coordinate_y
        self.measured_volume: float = measured_volume

    @staticmethod
    def from_json(data: dict, config):
        """Reads data from a JSON object and returns a new room calibration point instance.

        :param dict data: JSON data
        :param config.Config config: Config instance
        :returns: Room Calibration Point
        :rtype: RoomCalibrationPoint
        """
        speaker = config.speaker_repository.get_speaker(data.get('speaker_id'))
        return RoomCalibrationPoint(speaker, data.get('coordinateX'), data.get('coordinateY'), data.get('measuredVolume'))

    def to_json(self, recursive: bool = False) -> dict:
        """Creates a JSON serializable object.

        :param bool recursive: If true, all relations will be returned as full objects as well.
                               If false, only the ids of the relations will be returned.
        :returns: JSON serializable object
        :rtype: dict
        """

        json = {
            'coordinateX': self.coordinate_x,
            'coordinateY': self.coordinate_y,
            'measuredVolume': self.measured_volume,
        }

        if recursive:
            json['speaker'] = self.speaker.to_json()
        else:
            json['speaker_id'] = self.speaker.speaker_id

        return json