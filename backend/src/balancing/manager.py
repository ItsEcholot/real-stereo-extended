"""Handles sonos discovery and control."""

from config import Config
from .sonos import Sonos


class BalancingManager:
    """The BalancingManager controls Sonos speaker discovery and control threads"""

    def __init__(self, config: Config):
        self.config = config
        self.sonos = Sonos(config)

    async def start_discovery(self) -> None:
        """Start the discovery loop"""
        print('[Balancing] Starting sonos discovery loop')
        await self.sonos.discover_loop()

    def stop_discovery(self) -> None:
        """Stop the discovery loop"""
        print('[Balancing] Stopping sonos discovery loop')
        self.sonos.stop_discover_loop()
