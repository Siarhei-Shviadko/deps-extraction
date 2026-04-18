from typing import Optional

from .....exceptions import InconsistentProfileDescription
from ....shared import Guard, ImmutableCheck
from .description import Description, FieldDescription
from .field_type import FieldType

__all__ = ["FieldProfile"]


class FieldProfile:
    type = Guard[FieldType](FieldType, ImmutableCheck())
    description = Guard[FieldDescription](FieldDescription, ImmutableCheck())

    def __init__(self, type_: FieldType, description: Optional[Description] = None) -> None:
        self.type = type_
        self.description = description if description is not None else FieldDescription()

        self._validate_profile()

    def _validate_profile(self) -> None:
        if not self.description.belongs_to_type(self.type):
            raise InconsistentProfileDescription(type_=self.type, desc_class_name=self.description.__class__.__name__)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.description == other.description and self.type == other.type

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}': " f"{self.type = }, " f"{self.description = }>"

    def with_updated_description(self, description: FieldDescription) -> "FieldProfile":
        return FieldProfile(type_=self.type, description=description)
