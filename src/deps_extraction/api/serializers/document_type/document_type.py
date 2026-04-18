from typing import Optional

from pydantic import Field

from deps_extraction.domain.model import DocumentType, ExtractionType

from ..configured_base_serializer import ConfiguredBaseSerializer
from .field import SerializedField

__all__ = [
    "SerializedDocumentType",
    "SerializedDocumentTypes",
]


class SerializedDocumentType(ConfiguredBaseSerializer):
    id: str
    tenant_id: str = Field(alias="tenantId")
    document_type: str = Field(alias="documentType")
    extraction_type: Optional[ExtractionType] = Field(alias="extractorType")
    fields: list[SerializedField]

    @classmethod
    def from_model(cls, document_type: DocumentType) -> "SerializedDocumentType":
        return cls(
            id=document_type.id(),
            tenant_id=document_type.tenant_id(),
            document_type=document_type.name,
            extraction_type=None
            if document_type.extraction_type == ExtractionType.NON
            else document_type.extraction_type,
            fields=[
                SerializedField.from_model(
                    document_type_id=document_type.id(),
                    field=field,
                )
                for field in document_type.composite_fields
            ],
        )


class SerializedDocumentTypes(ConfiguredBaseSerializer):
    result: list[SerializedDocumentType]

    @classmethod
    def from_model(cls, document_types: list[DocumentType]) -> "SerializedDocumentTypes":
        return cls(result=[SerializedDocumentType.from_model(document_type) for document_type in document_types])
