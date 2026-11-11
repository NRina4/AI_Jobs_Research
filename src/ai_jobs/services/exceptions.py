class ReferenceNotFoundError(Exception):
    """Raised when a referenced database record does not exist."""

    def __init__(self, field_name: str, object_id: int):
        self.field_name = field_name
        self.object_id = object_id

        super().__init__(f"Referenced record not found: {field_name}={object_id}")
