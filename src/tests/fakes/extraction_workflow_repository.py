from typing import Any

from deps_extraction.domain.interfaces import IExtractionWorkflowRepository
from deps_extraction.domain.model import ExtractionWorkflow

__all__ = ["FakeExtractionWorkflowRepository"]


class FakeExtractionWorkflowRepository(IExtractionWorkflowRepository):
    def __init__(self) -> None:
        self._db: dict[str, Any] = {}

    def get(self, id_: str) -> ExtractionWorkflow | None:
        return self._db.get(id_)

    def save(self, workflow: ExtractionWorkflow) -> None:
        self._db[workflow.id()] = workflow
