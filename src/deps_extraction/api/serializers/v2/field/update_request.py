from typing import Optional

from pydantic import Field

from ...configured_base_serializer import ConfiguredBaseSerializer
from ...document_type.profile.description import SerializedDescription

__all__ = ["UpdateFieldRequest", "UpdateFieldsRequest"]


class UpdateFieldRequest(ConfiguredBaseSerializer):
    name: Optional[str] = None
    description: Optional[SerializedDescription] = None
    required: Optional[bool] = None
    read_only: Optional[bool] = Field(default=None, alias="readOnly")
    confidential: Optional[bool] = None
    order: Optional[int] = None


class UpdateFieldWithCodeRequest(UpdateFieldRequest):
    code: str


class UpdateFieldsRequest(ConfiguredBaseSerializer):
    fields: list[UpdateFieldWithCodeRequest]
