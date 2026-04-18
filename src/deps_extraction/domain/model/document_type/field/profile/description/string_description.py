from typing import Any, Optional

from .....shared import Guard, ImmutableCheck, RangeCheck
from ..field_type import FieldType
from .char_type import CharType
from .description import FieldDescription

__all__ = ["StringFieldDescription"]


class StringFieldDescription(FieldDescription):
    char_type = Guard[CharType](CharType, ImmutableCheck())
    char_whitelist = Guard[str](str, ImmutableCheck())
    char_blacklist = Guard[str](str, ImmutableCheck())
    display_char_limit = Guard[int](int, ImmutableCheck(), RangeCheck(min_value=0))

    def __init__(
        self,
        char_type: Optional[CharType] = None,
        char_whitelist: Optional[str] = None,
        char_blacklist: Optional[str] = None,
        display_char_limit: Optional[int] = None,
    ) -> None:
        if char_type is not None:
            self.char_type = char_type
        if char_whitelist is not None:
            self.char_whitelist = char_whitelist
        if char_blacklist is not None:
            self.char_blacklist = char_blacklist
        if display_char_limit is not None:
            self.display_char_limit = display_char_limit

    def belongs_to_type(self, type_: FieldType) -> bool:
        return type_ in {FieldType.STRING, FieldType.CHECKMARK}

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)  # noqa: WPS222
            and other.char_type == self.char_type
            and other.char_whitelist == self.char_whitelist
            and other.char_blacklist == self.char_blacklist
            and other.display_char_limit == self.display_char_limit
        )

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__name__}': "
            f"{self.char_type = }, "
            f"{self.char_whitelist = }, "
            f"{self.char_blacklist = }, "
            f"{self.display_char_limit = }>"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "char_type": self.char_type,
            "char_whitelist": self.char_whitelist,
            "char_blacklist": self.char_blacklist,
            "display_char_limit": self.display_char_limit,
        }
