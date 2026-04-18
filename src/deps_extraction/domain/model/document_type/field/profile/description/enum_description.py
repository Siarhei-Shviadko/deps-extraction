from typing import Any

from .....shared import Guard, ImmutableCheck
from ..field_type import FieldType
from .description import FieldDescription

__all__ = ["EnumFieldDescription"]


class EnumFieldDescription(FieldDescription):
    options = Guard[list[str]](list, ImmutableCheck())

    def __init__(self, options: list[str]) -> None:
        self.options = options

    def belongs_to_type(self, type_: FieldType) -> bool:
        return type_ == FieldType.ENUM

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and len(self.options) == len(other.options)
            and sorted(self.options) == sorted(other.options)
        )

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}': " f"{self.options = }>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "options": self.options,
        }
