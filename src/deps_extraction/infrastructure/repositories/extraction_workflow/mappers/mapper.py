from typing import Any

from sqlalchemy.engine.result import RowProxy

from deps_extraction.domain.model import EntityId, ExtractionWorkflow

from .step_mapper import ExtractionStepMapper

__all__ = ["ExtractionWorkflowMapper"]


class ExtractionWorkflowMapper:
    @classmethod
    def to_dict(cls, workflow: ExtractionWorkflow) -> dict[str, Any]:
        return {
            "id": workflow.id(),
            "document_id": workflow.document_id,
            "steps": [ExtractionStepMapper.to_dict(step) for step in workflow.steps],
            "current_step_index": workflow.current_step_index,
        }

    @classmethod
    def from_raw(cls, raw_workflow: RowProxy) -> ExtractionWorkflow:
        return ExtractionWorkflow(
            id_=EntityId(raw_workflow["id"]),
            document_id=raw_workflow["document_id"],
            steps=[ExtractionStepMapper.from_raw(step) for step in raw_workflow["steps"]],
            current_step_index=raw_workflow["current_step_index"],
        )
