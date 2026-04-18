from ....shared import Guard, ImmutableCheck
from .error_type import ErrorType

__all__ = ["ExtractionStepError"]


class ExtractionStepError:
    error_type = Guard[ErrorType](ErrorType, ImmutableCheck())
    error_message = Guard[str](str, ImmutableCheck())

    def __init__(self, error_type: ErrorType, error_message: str) -> None:
        self.error_type = error_type
        self.error_message = error_message

    def __str__(self) -> str:
        return f"{self.error_type.capitalize()} Error: {self.error_message}"

    def __repr__(self) -> str:
        return (
            f"ExtractionStepError("
            f"error_type=ErrorType.{self.error_type.name}, "
            f"error_message={repr(self.error_message)})"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.error_type == other.error_type
            and self.error_message == other.error_message
        )
