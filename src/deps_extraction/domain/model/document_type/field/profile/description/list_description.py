from typing import Any, Optional

from .....shared import Guard, ImmutableCheck
from ..field_type import FieldType
from .description import FieldDescription

__all__ = ["ListFieldDescription"]


class ListFieldDescription(FieldDescription):
    item_type = Guard[FieldType](FieldType, ImmutableCheck())
    item_type_data = Guard[FieldDescription](FieldDescription, ImmutableCheck())

    def __init__(
        self,
        item_type: FieldType,
        item_type_data: Optional[FieldDescription] = None,
    ) -> None:
        self.item_type = item_type
        if item_type_data is not None:
            self.item_type_data = item_type_data

    def belongs_to_type(self, type_: FieldType) -> bool:
        return type_ == FieldType.LIST

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)  # noqa: WPS222
            and other.item_type == self.item_type
            and other.item_type_data == self.item_type_data
        )

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}': " f"{self.item_type = }, " f"{self.item_type_data = }>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_type": self.item_type,
            "base_type_data": self.item_type_data.to_dict() if self.item_type_data else None,
        }
