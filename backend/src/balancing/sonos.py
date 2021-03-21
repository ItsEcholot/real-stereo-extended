"""Implements Sonos discovery and control"""
from time import sleep
from config import Config
import soco


class Sonos:
    """Performs discovery for Sonos speakers and sends messages to control them."""

    def __init__(self, config: Config):
        self.discover_loop_exiting = False
        self.config = config

    def discover_loop(self):
        """Starts the discover loop which runs every 15 seconds until stopped"""
        self.discover_loop_exiting = False
        while not self.discover_loop_exiting:
            zones = soco.discover()
            print(zones)
            sleep(15)

    def stop_discover_loop(self):
        """Sets the flag to stop the discover loop"""
        self.discover_loop_exiting = True
