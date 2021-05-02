"""Controller for the /balances namespace."""

from typing import List
from socketio import AsyncNamespace
from models.speaker import Speaker


class BalancesController(AsyncNamespace):
    """Controller for the /balances namespace."""

    def __init__(self):
        super().__init__(namespace='/balances')
        self.connections = 0

    def on_connect(self, _, __) -> None:
        """On client connect."""
        self.connections += 1

    def on_disconnect(self, _) -> None:
        """On client disconnect."""
        self.connections -= 1

    async def send_balances(self, speakers: List[Speaker], volumes: List[int]) -> None:
        """Sends the current balances to all clients.

        :param List[Speaker] speakers: All speakers
        :param List[int] volumes: Volumes for the speakers
        """
        if self.connections < 1:
            return

        balances = []

        for index, speaker in enumerate(speakers):
            balances.append({
                'volume': volumes[index],
                'speaker': speaker.to_json(recursive=True)
            })

        await self.emit('get', balances)
