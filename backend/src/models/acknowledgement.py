"""Acknowledgment holds the response to a create/update/delete API event."""


class Acknowledgement:
    """Acknowledgment holds the response to a create/update/delete API event."""

    def __init__(self):
        self.successful: bool = True
        self.created_id: int = None
        self.errors: list = []

    def add_error(self, error: str) -> None:
        """Adds an error to the response. It will also set `successful` to False.

        :param str error: Error message
        """
        self.successful = False
        self.errors.append(error)

    def to_json(self) -> dict:
        """Creates a JSON serializable object.

        :returns: JSON serializable object
        :rtype: dict
        """
        json = {
            'successful': self.successful,
        }

        if self.created_id is not None:
            json['createdId'] = self.created_id

        if len(self.errors) > 0:
            json['errors'] = self.errors

        return json
