from typing import Any, Optional

from .....shared import Guard, ImmutableCheck, RangeCheck
from ..field_type import FieldType
from .description import FieldDescription

__all__ = ["DateFieldDescription"]


class DateFieldDescription(FieldDescription):
    format = Guard[str](str, ImmutableCheck())
    display_char_limit = Guard[int](int, ImmutableCheck(), RangeCheck(min_value=0))

    def __init__(self, format: str, display_char_limit: Optional[int] = None) -> None:  # noqa: WPS125
        self.format = format
        if display_char_limit is not None:
            self.display_char_limit = display_char_limit

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": self.format,
            "display_char_limit": self.display_char_limit,
        }

    def belongs_to_type(self, type_: FieldType) -> bool:
        return type_ == FieldType.DATE

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.format == other.format
            and self.display_char_limit == other.display_char_limit
        )

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}': " f"{self.format = }, " f"{self.display_char_limit = }>"
