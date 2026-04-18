from typing import Optional, TypedDict

from .field import RawField

__all__ = ["RawDocumentType"]


class RawDocumentType(TypedDict):
    document_type_id: str
    tenant_id: str
    name: str
    extraction_type: str
    fields: Optional[list[RawField]]
