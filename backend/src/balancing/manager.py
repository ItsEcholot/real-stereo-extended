"""Handles sonos discovery and control."""
from threading import Thread
from config import Config
from .sonos import Sonos


class BalancingManager:
    """The BalancingManager controls Sonos speaker discovery and control threads"""

    def __init__(self, config: Config):
        self.config = config
        self.sonos = Sonos(config)
        self.discover_thread = None
        self.control_thread = None

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

    def start_control(self) -> None:
        """Start the control loop"""
        if self.control_thread is not None:
            return
        print('[Balancing] Starting sonos control loop')
        self.control_thread = Thread(target=self.sonos.control_loop)
        self.control_thread.start()

    def stop_control(self) -> None:
        """Stop the control loop"""
        if self.control_thread is not None:
            print('[Balancing] Stopping sonos control loop')
            self.sonos.stop_control_loop()
            self.control_thread.join()
            self.control_thread = None
