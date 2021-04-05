"""Containes a single calibration point for a room"""

from models.speaker import Speaker

class RoomCalibrationPoint:
    """Containes a single calibration point for a room and a speaker
    
    :param models.speaker.Speaker speaker: Speaker which was playing the test sound
    :param int coordinate_x: The x coordinate of the calibration point
    :param int coordinate_y: The y coordinate of the calibration point
    :param float measured_volume_low: The measured volume of the low volume sample
    :param float measured_volume_high: The measured volume of the high volume sample
    """
    def __init__(self, speaker: Speaker, coordinate_x: int, coordinate_y: int, 
                 measured_volume_low: float, measured_volume_high: float):
        self.speaker: Speaker = speaker
        self.coordinate_x: int = coordinate_x
        self.coordinate_y: int = coordinate_y
        self.measured_volume_low: float = measured_volume_low
        self.measured_volume_high: float = measured_volume_high

    def to_json(self, recursive: bool = False) -> dict:
        """Creates a JSON serializable object.

        :param bool recursive: If true, all relations will be returned as full objects as well.
                               If false, only the ids of the relations will be returned.
        :returns: JSON serializable object
        :rtype: dict
        """

        json = {
            'coordinate_x': self.coordinate_x,
            'coordinate_y': self.coordinate_y,
            'measured_volume_low': self.measured_volume_low,
            'measured_volume_high': self.measured_volume_high,
        }

        if recursive:
            json['speaker'] = self.speaker.to_json()
        else:
            json['speaker_id'] = self.speaker.speaker_id

        return json