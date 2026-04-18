from typing import Optional

from pydantic import Field

from deps_extraction.domain.model import DEFAULT_FIELD_ORDER, FieldType

from ...configured_base_serializer import ConfiguredBaseSerializer
from ...document_type.profile.description import SerializedDescription

__all__ = ["CreateFieldRequest"]


class CreateFieldRequest(ConfiguredBaseSerializer):
    name: str
    type: FieldType
    description: Optional[SerializedDescription] = Field(default=None)
    required: bool
    confidential: bool = Field(default=False)
    read_only: bool = Field(default=False, alias="readOnly")
    order: Optional[int] = Field(default=DEFAULT_FIELD_ORDER)
    extractor_id: Optional[str] = Field(default=None, alias="extractorId")
    code: Optional[str] = Field(default=None)
