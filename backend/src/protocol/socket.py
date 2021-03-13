"""Base socket logic and message parsing."""

import re
from threading import Thread
from .cluster_pb2 import Wrapper
from .constants import APP, VERSION, BUFFER_SIZE


class ClusterSocket:
    """Base socket logic and message parsing."""

    def __init__(self):
        self.message_type_pattern = re.compile(r'(?<!^)(?=[A-Z])')
        self.thread = None
        self.running = False

    def start(self) -> None:
        """Starts the socket in a new thread."""
        self.thread = Thread(target=self.init)
        self.thread.start()

    def stop(self) -> None:
        """Stops the socket."""
        self.running = False
        self.thread.join()

    def init(self) -> None:
        """This method should be overwritten by the children class."""

    def build_message(self):  # pylint: disable=no-self-use
        """Builds a new message object.

        :returns: Message wrapper
        :rtype: protocol.cluster_pb2.Wrapper
        """
        wrapper = Wrapper()
        wrapper.app = APP
        wrapper.version = VERSION

        return wrapper

    def receive_message(self, socket, call_events: bool = True) -> (Wrapper, str):
        """Waits until the next message and parses it.

        :param socket socket: Listening socket
        :param bool call_events: If true, the `on_` events will be called on the class.
        :returns: Message and the sending IP
        :rtype: (protocol.cluster_pb2.Wrapper, str)
        """
        try:
            data, address = socket.recvfrom(BUFFER_SIZE)
            message = Wrapper()
            message.ParseFromString(data)

            # ignore message if it is not from real stereo
            if message.app != APP:
                return None, address[0]

            if call_events:
                self.call_events(message, address[0])

            return message, address[0]
        except RuntimeError as error:
            print(error)
            return None, None

    def call_events(self, message: Wrapper, address: str) -> None:
        """Calls the `on_` events on the class for the given message.
        For example, when a ServiceAnnouncement has been received, the `on_service_announcement`
        method will be called with the two parameters `message: Wrapper` and `address: str`.

        :param protocol.cluster_pb2.Wrapper message: Received message
        :param str address: IP address of sender
        """
        message_type = message.WhichOneof('message')

        # convert camelCase to snake_case
        message_type = self.message_type_pattern.sub('_', message_type).lower()

        # check if the event has been implemented
        event = 'on_' + message_type
        event_method = getattr(self, event)

        if event_method is not None:
            event_method(message, address)
