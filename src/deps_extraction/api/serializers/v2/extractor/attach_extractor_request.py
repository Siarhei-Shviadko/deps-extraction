from typing import Optional

from pydantic import Field, field_validator

from deps_extraction.domain.model import ExtractorType

from ...configured_base_serializer import ConfiguredBaseSerializer
from ...document_type import SerializedField

__all__ = ["AttachExtractorRequest"]


NON_EXTRACTOR_DEFINITION = "non"


class AttachExtractorRequest(ConfiguredBaseSerializer):
    name: str
    extractor_type: Optional[ExtractorType] = Field(
        default=None,
        alias="extractorType",
    )
    engine: Optional[str] = None
    language: Optional[str] = None
    image_transformations: Optional[list[str]] = Field(None, alias="imageTransformations")
    fields: Optional[list[SerializedField]] = Field(default_factory=list)
    description: Optional[str] = Field(None, max_length=100)
    extractor_id: Optional[str] = Field(None, alias="extractorId")

    @field_validator("extractor_type", mode="before")
    @classmethod
    def convert_extractor_type(cls, value: str) -> Optional[ExtractorType]:
        if value == NON_EXTRACTOR_DEFINITION:
            return None
        return ExtractorType(value)
