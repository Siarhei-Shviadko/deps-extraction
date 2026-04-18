from typing import Any, Optional
from uuid import uuid4

from ..shared import EntityId, ExtractorType
from .extraction_step import ExtractionStep, ExtractionStepFactory
from .extraction_workflow import ExtractionWorkflow

__all__ = ["ExtractionWorkflowBuilder"]


class ExtractionWorkflowBuilder:
    def __init__(
        self,
        document_id: str,
        tenant_id: str,
        document_type_id: str,
        command_channel: str,
        correlation_headers: dict[str, str],
        extra_headers: dict[str, Any],
        template_version_id: Optional[str] = None,
        language: Optional[str] = None,
        engine: Optional[str] = None,
        llm_type: Optional[str] = None,
    ) -> None:
        self._document_id = document_id
        self._tenant_id = tenant_id
        self._document_type_id = document_type_id
        self._command_channel = command_channel
        self._correlation_headers = correlation_headers
        self._extra_headers = extra_headers
        self._template_version_id = template_version_id
        self._language = language
        self._engine = engine
        self._llm_type = llm_type

        self._id = uuid4().hex

        self._step_factory = self._initialize_step_factory()
        self._steps: list[ExtractionStep] = []

    def with_step_for(self, extractor_id: str, extractor_type: ExtractorType) -> "ExtractionWorkflowBuilder":
        self._steps.append(self._step_factory.make_for(extractor_id=extractor_id, extractor_type=extractor_type))
        return self

    def build(self) -> ExtractionWorkflow:
        if not self._steps:
            raise ValueError("Cann't build ExtractionWorkflow without steps")

        self._steps.append(self._step_factory.make_reply_extraction())

        return ExtractionWorkflow(
            id_=EntityId(self._id),
            document_id=self._document_id,
            steps=self._steps,
        )

    def _initialize_step_factory(self) -> ExtractionStepFactory:
        return ExtractionStepFactory(
            workflow_id=self._id,
            tenant_id=self._tenant_id,
            document_id=self._document_id,
            document_type_id=self._document_type_id,
            command_channel=self._command_channel,
            correlation_headers=self._correlation_headers,
            template_version_id=self._template_version_id,
            language=self._language,
            engine=self._engine,
            llm_type=self._llm_type,
            extra_headers=self._extra_headers,
        )
