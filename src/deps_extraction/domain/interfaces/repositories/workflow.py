from abc import ABC, abstractmethod
from typing import Optional

from ...model import ExtractionWorkflow

__all__ = ["IExtractionWorkflowRepository"]


class IExtractionWorkflowRepository(ABC):
    @abstractmethod
    def get(self, id_: str) -> Optional[ExtractionWorkflow]:
        pass

    @abstractmethod
    def save(self, workflow: ExtractionWorkflow) -> None:
        pass
