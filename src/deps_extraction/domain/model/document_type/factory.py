from typing import Optional

from ..shared import DocumentTypeId, ExtractionType, ExtractorType, TenantId
from .document_type import DocumentType
from .field import FieldType, RawField

__all__ = ["DocumentTypeFactory"]


class DocumentTypeFactory:
    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        id_: Optional[str] = None,
        extraction_type: Optional[str] = None,
        fields: Optional[list[RawField]] = None,
    ) -> DocumentType:
        document_type = DocumentType(
            id_=DocumentTypeId(id_),
            tenant_id=TenantId(tenant_id),
            name=name,
            extraction_type=ExtractionType.NON,
        )

        if extraction_type and extraction_type != ExtractionType.NON:
            attached_extractor = document_type.attach_extractor(
                type_=ExtractorType(extraction_type),
                fields=[],
            )

            for field in fields or []:
                document_type.add_field(
                    name=field["name"],
                    type_=FieldType(field["field_type"]),
                    required=field["required"],
                    confidential=field.get("confidential"),
                    read_only=field.get("read_only"),
                    description=field.get("description"),
                    code=field.get("code"),
                    extractor_id=attached_extractor.id(),
                )

        return document_type
