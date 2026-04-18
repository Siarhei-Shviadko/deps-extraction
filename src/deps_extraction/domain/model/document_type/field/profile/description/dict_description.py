from typing import Any, Optional

from .....shared import Guard, ImmutableCheck
from ..field_type import FieldType
from .description import FieldDescription

__all__ = ["DictFieldDescription"]


class DictFieldDescription(FieldDescription):
    key_type = Guard[FieldType](FieldType, ImmutableCheck())
    key_meta = Guard[FieldDescription](FieldDescription, ImmutableCheck())
    value_type = Guard[FieldType](FieldType, ImmutableCheck())
    value_meta = Guard[FieldDescription](FieldDescription, ImmutableCheck())

    def __init__(
        self,
        key_type: FieldType,
        value_type: FieldType,
        key_meta: Optional[FieldDescription] = None,
        value_meta: Optional[FieldDescription] = None,
    ) -> None:
        self.key_type = key_type
        if key_meta is not None:
            self.key_meta = key_meta

        self.value_type = value_type
        if value_meta is not None:
            self.value_meta = value_meta

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_type": self.key_type,
            "key_data": self.key_meta.to_dict() if self.key_meta else None,
            "value_type": self.value_type,
            "value_data": self.value_meta.to_dict() if self.value_meta else None,
        }

    def belongs_to_type(self, type_: FieldType) -> bool:
        return type_ == FieldType.DICT

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.key_type == other.key_type
            and self.key_meta == other.key_meta
            and self.value_type == other.value_type
            and self.value_meta == other.value_meta
        )

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__name__}': "
            f"{self.key_type = }, "
            f"{self.key_meta = }, "
            f"{self.value_type = }, "
            f"{self.value_meta = }>"
        )
