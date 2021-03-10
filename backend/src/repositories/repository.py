"""Base repository class containing the listener logic."""


class Repository:
    """Base repository class containing the listener logic."""

    def __init__(self):
        self.listeners = []

    def register_listener(self, listener: callable) -> None:
        """Register a new listener on the repository.

        :param callable listener: Listener function without any arguments
        """
        self.listeners.append(listener)

    def call_listeners(self) -> None:
        """Calls all registered listeners."""
        for listener in self.listeners:
            listener()
