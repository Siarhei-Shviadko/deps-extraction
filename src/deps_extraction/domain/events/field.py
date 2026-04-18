from dataclasses import dataclass
from typing import Any, Optional

from deps_message_flow.events.common import DomainEvent

from ..types import RawDescription, RawTableDescription

__all__ = [
    "ExtractorFieldCreated",
    "ExtractorFieldUpdated",
    "ExtractorFieldDeleted",
    "ExtractorFieldsDuplicated",
    "CloudExtractorFieldCreated",
    "CloudExtractorFieldDeleted",
    "CloudExtractorFieldUpdated",
    "ExtractionFieldsMoved",
]


@dataclass
class ExtractorFieldCreated(DomainEvent):
    code: str
    name: str
    document_type_code: str
    extractor_id: str
    extractor_type: str
    field_type: str
    required: bool
    order: int
    confidential: bool
    read_only: bool
    description: Optional[dict[str, Any]]

    def __post_init__(self):
        self.description = self.description.to_dict() if self.description else None


@dataclass
class ExtractorFieldUpdated(ExtractorFieldCreated):
    pass


@dataclass
class ExtractorFieldDeleted(DomainEvent):
    code: str
    document_type_code: str
    extractor_type: str
    extractor_id: str


@dataclass
class ExtractorFieldsDuplicated(DomainEvent):
    source_document_type_code: str
    target_document_type_code: str


@dataclass
class CloudExtractorFieldCreated(DomainEvent):
    document_type_id: str
    code: str
    name: str
    type: str
    description: Optional[RawDescription]
    required: bool = False
    order: int = 0


@dataclass
class CloudExtractorFieldUpdated(DomainEvent):
    document_type_id: str
    code: str
    description: RawTableDescription


@dataclass
class CloudExtractorFieldDeleted(DomainEvent):
    document_type_id: str
    code: str


@dataclass
class ExtractionFieldsMoved(DomainEvent):
    document_type_id: str
    source_extractor_id: str
    target_extractor_id: str
    fields_codes: list[str]
