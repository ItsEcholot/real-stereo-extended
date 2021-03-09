class Acknowledgement:
    def __init__(self):
        self.successful: bool = True
        self.created_id: int = None
        self.errors: list = []

    def add_error(self, error: str) -> None:
        self.successful = False
        self.errors.append(error)

    def to_json(self) -> dict:
        json = {
            'successful': self.successful,
        }

        if self.created_id is not None:
            json['createdId'] = self.created_id

        if len(self.errors) > 0:
            json['errors'] = self.errors

        return json
