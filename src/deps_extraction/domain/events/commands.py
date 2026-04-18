from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict

from deps_message_flow.commands.common import Command

from ..model.shared import CloudNativeExtractors

__all__ = [
    "GetDocumentTypes",
    "GetDocumentTypesReply",
    "ExtractDocument",
    "PerformExtraction",
    "PerformExtractionReply",
    "PerformPrototypeExtraction",
    "PerformTemplateExtraction",
    "PerformCloudNativeExtraction",
    "PerformLLMExtraction",
    "PerformExtractionStepReply",
]


@dataclass
class ExtractDocument(Command):
    document_id: str
    language: Optional[str] = None
    engine: Optional[str] = None


class GetDocumentTypes(Command):
    pass  # noqa: WPS604


@dataclass
class GetDocumentTypesReply(Command):
    document_types: list[dict[str, Any]]


class ExtraData(TypedDict, total=False):
    template_version_id: Optional[str]


@dataclass
class PerformExtraction(Command):
    tenant_id: str
    document_id: str
    document_type_id: str
    language: Optional[str] = None
    engine: Optional[str] = None
    llm_type: Optional[str] = None
    extra_data: ExtraData = field(default_factory=dict)  # type: ignore


@dataclass
class PerformExtractionReply(Command):
    error_type: Optional[str]
    error_message: Optional[str]


@dataclass
class PerformExtractionStepReply(Command):
    error_type: Optional[str]
    error_message: Optional[str]


@dataclass
class PerformPrototypeExtraction(Command):
    prototype_id: str
    tenant_id: str
    document_id: int
    language: Optional[str] = None
    engine: Optional[str] = None


@dataclass
class PerformTemplateExtraction(Command):
    template_id: str
    tenant_id: str
    document_id: int
    version_id: Optional[str] = None
    language: Optional[str] = None
    engine: Optional[str] = None


@dataclass
class PerformCloudNativeExtraction(Command):
    extractor_type: CloudNativeExtractors
    extractor_id: str
    document_id: str


@dataclass
class PerformLLMExtraction(Command):
    extractor_id: str
    document_id: str
    llm_type: Optional[str] = None
