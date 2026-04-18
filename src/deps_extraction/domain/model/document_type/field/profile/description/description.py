from typing import Any

from ..field_type import FieldType

__all__ = ["FieldDescription"]


class FieldDescription:
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}>"

    def belongs_to_type(self, _: FieldType) -> bool:
        return True

    def to_dict(self) -> dict[str, Any]:
        return {}
