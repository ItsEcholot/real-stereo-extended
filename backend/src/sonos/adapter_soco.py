"""Defines methods to send commands to Sonos speakers using the soco library"""
from typing import Set, List
from models.speaker import Speaker
import soco
from soco import events_asyncio
from soco.snapshot import Snapshot
from soco.events_asyncio import Subscription
from .adapter import SonosAdapter


soco.config.EVENTS_MODULE = events_asyncio


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

    def get_volume(self, speaker: Speaker) -> int:
        """Gets volume of passed Sonos speaker

        :param models.speaker.Speaker speaker: Speaker for which the volume gets requested
        """
        soco_instance = soco.SoCo(speaker.ip_address)
        return soco_instance.volume

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
        soco_instance.play_uri(uri=self.calibration_sound_uri, title='RS Calibration Sound')
        soco_instance.play_mode = 'REPEAT_ONE'

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
        if not hasattr(soco_instance, 'snapshot'):
            raise ValueError(
                'Instance doesn\'t contain a snapshot... Did you call save_snapshot before restoring?')
        soco_instance.snapshot.restore()

    async def subscribe(self, speaker: Speaker, event_handler: callable):
        """Subscribe to sonos events

        :param models.speaker.Speaker speaker: Register event handler for this speaker
        :param callable event_handler: Function that will receive the events
        :returns: Subscription with the master ip
        :rtype: (soco.events_asyncio.Subscription, str)
        """
        coordinator = self.get_coordinator_instance(speaker)
        subscription = Subscription(coordinator.renderingControl, event_handler)
        await subscription.subscribe(requested_timeout=60*60*24, auto_renew=True)

        return (subscription, coordinator.ip_address)

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

    def ensure_speakers_in_group(self, speakers: List[Speaker]):
        """Ensures that all the passed speakers are in a group together.
        First checking if any speaker is already part of a group and if so
        adding all the other speakers to that group. If that isn't the case
        a new group is created and the first speaker of the list is selected
        as the coordinator.

        :param list[models.speaker.Speaker] speakers: Speakers to add to a single group
        """
        biggest_group = None
        biggest_group_size = 0

        # find biggest group with only the passed speakers in it
        for speaker in speakers:
            soco_instance = soco.SoCo(speaker.ip_address)
            if soco_instance.is_visible and soco_instance.group is not None:
                group_size = len(soco_instance.group.members)
                group_pure = True
                for group_speaker in soco_instance.group:
                    if not any(x.speaker_id == group_speaker.uid for x in speakers):
                        group_pure = False
                if group_pure and group_size > biggest_group_size:
                    biggest_group_size = group_size
                    biggest_group = soco_instance.group

        # add all other speakers to this group
        for speaker in speakers:
            soco_instance = soco.SoCo(speaker.ip_address)
            if not any(x.uid == speaker.speaker_id for x in biggest_group.members):
                print('[SoCo Adapter] Adding {} to the group of {}'.format(
                    speaker.ip_address, biggest_group.coordinator.ip_address))
                if soco_instance.group is not None:
                    soco_instance.previous_group_coordinator = soco_instance.group.coordinator
                soco_instance.join(biggest_group.coordinator)

    def restore_speakers_groups(self, speakers: List[Speaker]):
        """Restores the previous group state like it was before
        calling ensure_speakers_in_group

        :param list[models.speaker.Speaker] speaker: Speaker to control
        """
        for speaker in speakers:
            soco_instance = soco.SoCo(speaker.ip_address)
            if hasattr(soco_instance, 'previous_group_coordinator'):
                print('[SoCo Adapter] Adding {} to the group of {}'.format(
                    speaker.ip_address, soco_instance.previous_group_coordinator.ip_address))
                if soco_instance.previous_group_coordinator != soco_instance:
                    soco_instance.join(soco_instance.previous_group_coordinator)
                else:
                    soco_instance.unjoin()
