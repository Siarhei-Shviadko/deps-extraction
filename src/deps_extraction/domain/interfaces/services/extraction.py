from abc import ABC, abstractmethod
from typing import Any, Optional

__all__ = ["IExtractionService"]


class IExtractionService(ABC):
    @abstractmethod
    def extract(
        self,
        document_id: int,
        document_type_id: str,
        language: Optional[str] = None,
        engine: Optional[str] = None,
        extra_headers: Optional[dict[str, Any]] = None,
    ) -> None:
        pass
