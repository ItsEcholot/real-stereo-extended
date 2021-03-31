"""Defines methods to send commands to Sonos speakers using the soco library"""
from typing import Set
from models.speaker import Speaker
import soco
from soco.snapshot import Snapshot
from .adapter import SonosAdapter


class SonosSocoAdapter(SonosAdapter):
    """Defines methods to send commands to Sonos speakers using the soco library"""

    def discover(self) -> Set[Speaker]:
        """Discovers local Sonos speakers

        :returns: Set of discovered speakers
        :rtype: set[models.speaker.Speaker]
        """
        speakers = set()
        speaker: soco.SoCo
        discovery = soco.discover(include_invisible=True)
        if discovery is not None:
            for speaker in discovery:
                name = speaker.player_name
                speaker_instance = Speaker(speaker_id=speaker.uid,
                                           name=name, ip_address=speaker.ip_address)
                if not speaker.is_visible and len({x for x in speaker.group if x.is_visible and x.player_name == name}) == 1:
                    speaker_instance.name = name + ' (R)'
                elif len(self.get_stereo_pair_slaves(speaker)) == 1:
                    speaker_instance.name = name + ' (L)'
                speakers.add(speaker_instance)
        return speakers

    def set_volume(self, speaker: Speaker, volume: int):
        """Sets volume for passed Sonos speaker

        :param models.speaker.Speaker speaker: Speaker to control
        :param int volume: Volume to set
        """
        soco_instance = soco.SoCo(speaker.ip_address)
        soco_slaves = list(self.get_stereo_pair_slaves(speaker))
        soco_slaves_volumes = [x.volume for x in soco_slaves]
        soco_instance.volume = volume
        for index, slave in enumerate(soco_slaves):
            slave.volume = soco_slaves_volumes[index]

    def ramp_to_volume(self, speaker: Speaker, volume: int):
        """Ramps volume to target volume for the passed Sonos speaker

        :param models.speaker.Speaker speaker: Speaker to control
        :param int volume: Volume to ramp up or down to
        """
        soco_instance = soco.SoCo(speaker.ip_address)
        soco_slaves = list(self.get_stereo_pair_slaves(speaker))
        soco_slaves_volumes = [x.volume for x in soco_slaves]
        soco_instance.ramp_to_volume(volume)
        for index, slave in enumerate(soco_slaves):
            slave.volume = soco_slaves_volumes[index]

    def play_calibration_sound(self, speaker: Speaker):
        """Plays the calibration sound on repeat on all speakers which are part
        of the passed speakers group.

        :param models.speaker.Speaker speaker: Speaker on which calibration sound should be played on
        """
        soco_instance = self.get_coordinator_instance(speaker)
        soco_instance.play_mode = 'REPEAT_ONE'
        soco_instance.play_uri(uri=self.calibration_sound_uri, title='RS Calibration Sound')

    def save_snapshot(self, speaker: Speaker):
        """Saves the current playback state of the passed speaker

        :param models.speaker.Speaker speaker: Speaker which playback state should be saved
        """
        soco_instance = self.get_coordinator_instance(speaker)
        soco_instance.snapshot = Snapshot(soco_instance)
        soco_instance.snapshot.snapshot()

    def restore_snapshot(self, speaker: Speaker):
        """Restores the last saved snapshot of the passed speaker

        :param models.speaker.Speaker speaker: Speaker whos last snapshot should be restored
        """
        soco_instance = self.get_coordinator_instance(speaker)
        if soco_instance.snapshot is None:
            raise ValueError(
                'Instance doesn\'t contain a snapshot... Did you call save_snapshot before restoring?')
        soco_instance.snapshot.restore()

    def get_coordinator_instance(self, speaker: Speaker) -> soco.SoCo:
        """Get the SoCo instance of the passed speaker or, if the passed speaker is in a
        group, get the groups coordinators SoCo instance.

        :param models.speaker.Speaker speaker: Speaker whos instance / coordinators instance should be returned
        :returns: SoCo instance or coordinators SoCo instance
        :rtype: soco.Soco
        """
        soco_instance = soco.SoCo(speaker.ip_address)
        if soco_instance.group is not None and soco_instance.group.coordinator is not None:
            soco_instance = soco_instance.group.coordinator
        return soco_instance

    def get_stereo_pair_slaves(self, speaker: Speaker) -> Set[soco.SoCo]:
        """Checks if the passed speaker is a stereo pair coordinator and
           returns the all speakers which could be a pair slave.

        :param models.speaker.Speaker speaker: Speaker to check
        :returns: Slave speaker of stereo pair
        :rtype: models.speaker.Speaker
        """
        soco_instance = soco.SoCo(speaker.ip_address)
        if not soco_instance.is_visible or soco_instance.group is None:
            return {}
        speaker_group: soco.groups.ZoneGroup = soco_instance.group
        return {x for x in speaker_group if not x.is_visible and
                x.player_name == soco_instance.player_name}
