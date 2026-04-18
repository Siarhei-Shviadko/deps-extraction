from typing import Optional, TypedDict

from . import FieldDescription

__all__ = ["RawField", "RawUpdateField"]


class RawField(TypedDict):
    name: str
    code: str
    required: bool
    field_type: str
    order: int
    confidential: Optional[bool]
    read_only: Optional[bool]
    description: Optional[FieldDescription]


class RawUpdateField(TypedDict):
    code: str
    name: Optional[str]
    required: Optional[bool]
    order: Optional[int]
    confidential: Optional[bool]
    read_only: Optional[bool]
    description: Optional[FieldDescription]
