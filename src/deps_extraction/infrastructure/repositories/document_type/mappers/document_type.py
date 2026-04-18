from typing import Any

from deps_extraction.domain.model import (
    DocumentType,
    DocumentTypeId,
    ExtractionType,
    TenantId,
)

from .extractor import ExtractorMapper

__all__ = ["DocumentTypeMapper"]


class DocumentTypeMapper:
    @staticmethod
    def to_dict(document_type: DocumentType) -> dict[str, Any]:
        return {
            "id": document_type.id(),
            "tenant_id": document_type.tenant_id(),
            "name": document_type.name,
            "extraction_type": document_type.extraction_type.value if document_type.extraction_type else None,
            "extractors": [
                ExtractorMapper.to_dict(extractor=extractor, document_type_id=document_type.id())
                for extractor in document_type.extractors.values()
            ],
        }

    @staticmethod
    def from_dict(document_type: dict[str, Any]) -> DocumentType:
        extraction_type = (
            ExtractionType(document_type["extraction_type"])
            if document_type["extraction_type"] is not None
            else ExtractionType.NON
        )
        extractors = {
            extractor["id"]: ExtractorMapper.from_dict(extractor) for extractor in document_type["extractors"]
        }

        return DocumentType(
            id_=DocumentTypeId(document_type["id"]),
            tenant_id=TenantId(document_type["tenant_id"]),
            name=document_type["name"],
            extractors=extractors,
            extraction_type=extraction_type,
        )
