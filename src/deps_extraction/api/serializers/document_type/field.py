from typing import Any, Optional

from pydantic import Field, field_validator

from deps_extraction.domain.model import CompositeField, FieldType

from ..configured_base_serializer import ConfiguredBaseSerializer
from .profile.description import DESCRIPTION_MAP, SerializedDescription

__all__ = ["SerializedField"]


class SerializedField(ConfiguredBaseSerializer):
    name: str
    code: str
    id: Optional[str] = Field(None, alias="pk")
    document_type_id: Optional[str] = Field(None, alias="documentTypeCode")
    required: bool = False
    order: Optional[int] = None
    field_type: FieldType = Field(alias="fieldType")
    confidential: bool = Field(default=False, alias="confidential")
    read_only: bool = Field(default=False, alias="readOnly")
    field_data: SerializedDescription = Field(..., alias="fieldMeta")

    @field_validator("field_data", mode="before")
    @classmethod
    def set_empty_if_none(cls, value: Optional[dict[str, Any]]) -> dict[str, Any]:
        return value or {}

    @classmethod
    def from_model(cls, document_type_id: str, field: CompositeField) -> "SerializedField":
        description_serializer = DESCRIPTION_MAP.get(field.profile.description.__class__)
        description = description_serializer.from_model(field.profile.description) if description_serializer else None

        return cls(
            id=field.code(),
            document_type_id=document_type_id,
            code=field.code(),
            name=field.name,
            field_type=field.profile.type,
            required=field.required,
            confidential=field.confidential,
            read_only=field.read_only,
            order=field.display_order,
            field_data=description,
        )
