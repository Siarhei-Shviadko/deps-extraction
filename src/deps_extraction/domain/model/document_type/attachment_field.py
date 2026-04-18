from dataclasses import dataclass
from typing import Any, Optional

from .composite_field import CompositeField
from .field import FieldDescription, FieldType

__all__ = ["FieldAttachment"]


@dataclass
class FieldAttachment:
    name: str
    code: str
    required: bool
    order: Optional[int]
    confidential: Optional[bool]
    read_only: Optional[bool]
    type: FieldType
    description: Optional[FieldDescription]

    def has_difference_with_composite_field(self, field: CompositeField) -> bool:
        def _has_updated_value(orig_value: Any, new_value: Any) -> bool:  # noqa: WPS430
            return new_value is not None and new_value != orig_value

        return (
            _has_updated_value(field.name, self.name)
            or _has_updated_value(field.required, self.required)
            or _has_updated_value(field.description, self.description)
            or _has_updated_value(field.display_order, self.order)
            or _has_updated_value(field.read_only, self.read_only)
            or _has_updated_value(field.confidential, self.confidential)
        )
