from typing import Optional

from pydantic import Field

from ...configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["AttachmentResponse"]


class AttachmentResponse(ConfiguredBaseSerializer):
    command_channel: Optional[str]
    document_type_id: str = Field(alias="documentTypeId")
    extractor_id: Optional[str] = Field(alias="extractorId")
