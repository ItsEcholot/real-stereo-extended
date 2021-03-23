"""Handles sonos discovery and control."""
from threading import Thread
from config import Config
from models.speaker import Speaker
from .sonos import Sonos


class BalancingManager:
    """The BalancingManager controls Sonos speaker discovery and control threads"""

    def __init__(self, config: Config):
        self.config = config
        self.sonos = Sonos(config)
        self.discover_thread = None

    def start_discovery(self) -> None:
        """Start the discovery loop"""
        if self.discover_thread is not None:
            return
        print('[Balancing] Starting sonos discovery loop')
        self.discover_thread = Thread(target=self.sonos.discover_loop)
        self.discover_thread.start()

    def stop_discovery(self) -> None:
        """Stop the discovery loop"""
        if self.discover_thread is not None:
            print('[Balancing] Stopping sonos discovery loop')
            self.sonos.stop_discover_loop()
            self.discover_thread.join()
            self.discover_thread = None
