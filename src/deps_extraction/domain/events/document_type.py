from dataclasses import dataclass
from typing import Optional

from deps_message_flow.events.common import DomainEvent

__all__ = [
    "DocumentDeleted",
    "DocumentTypeDeleted",
    "DocumentTypeChanged",
    "DocumentTypeCreated",
    "ExtractorAttached",
    "ExtractorDetached",
]


@dataclass
class DocumentDeleted(DomainEvent):
    document_id: int


@dataclass
class DocumentTypeDeleted(DomainEvent):
    document_type: str
    tenant: str


@dataclass
class DocumentTypeChanged(DomainEvent):
    document_id: int


@dataclass
class DocumentTypeCreated(DomainEvent):
    document_type: str
    tenant: str
    name: str


@dataclass
class ExtractorAttached(DomainEvent):
    extractor_id: str
    document_type_id: str
    extraction_type: str
    language: Optional[str] = None
    engine: Optional[str] = None
    description: Optional[str] = None
    image_transformations: Optional[list[str]] = None


@dataclass
class ExtractorDetached(DomainEvent):
    document_type_id: str
    extractor_id: str
    extractor_type: str
