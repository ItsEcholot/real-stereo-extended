"""Provides validation functions."""

from models.acknowledgment import Acknowledgment


class Validate:
    """Provides validation functions.

    :param models.acknowledgment.Acknowledgment ack: Acknowledgment instance for the current request
    """

    def __init__(self, ack: Acknowledgment):
        self.ack = ack

    def string(self, value: str, label: str, min_value: int = None, max_value: int = None) -> bool:
        """Validates if a value is a string and in the given boundaries.

        :param str value: Input value that should be validated
        :param str label: Label that will be shown in error messages
        :param int min_value: Min length (optional)
        :param int max_value: Max length (optional)
        :returns: Whether the input validates
        :rtype: bool
        """
        num_errors = len(self.ack.errors)

        if isinstance(value, str) is False:
            self.ack.add_error(label + ' must be a string')
        elif min_value == 1 and len(value) == 0:
            self.ack.add_error(label + ' must not be empty')
        elif min_value is not None and len(value) < min_value:
            self.ack.add_error(label + ' must be at least ' + str(min_value) + ' characters long')
        elif max_value is not None and len(value) > max_value:
            self.ack.add_error(label + ' must be at most ' + str(max_value) + ' characters long')

        return num_errors == len(self.ack.errors)

    def integer(self, value: int, label: str, min_value: int = None, max_value: int = None) -> bool:
        """Validates if a value is an integer and in the given boundaries.

        :param int value: Input value that should be validated
        :param str label: Label that will be shown in error messages
        :param int min_value: Min value (optional)
        :param int max_value: Max value (optional)
        :returns: Whether the input validates
        :rtype: bool
        """
        num_errors = len(self.ack.errors)

        if isinstance(value, int) is False:
            self.ack.add_error(label + ' must be an integer')
        elif min_value is not None and value < min_value:
            self.ack.add_error(label + ' must be at least ' + str(min_value))
        elif max_value is not None and value > max_value:
            self.ack.add_error(label + ' must be at most ' + str(max_value))

        return num_errors == len(self.ack.errors)

    def boolean(self, value: bool, label: str) -> None:
        """Validates if a value is a boolean.

        :param int value: Input value that should be validated
        :param str label: Label that will be shown in error messages
        :returns: Whether the input validates
        :rtype: bool
        """
        if isinstance(value, bool) is False:
            self.ack.add_error(label + ' must be a boolean')
            return False

        return True
