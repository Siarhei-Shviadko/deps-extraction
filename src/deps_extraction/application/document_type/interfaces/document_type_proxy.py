from abc import ABC, abstractmethod
from typing import Optional

__all__ = ["IDocumentTypeProxy"]


class IDocumentTypeProxy(ABC):  # noqa: WPS338
    @abstractmethod
    def create_document_type(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> str:
        ...  # noqa: WPS428

    @abstractmethod
    def delete_document_type(self, document_type_id: str) -> None:
        ...  # noqa: WPS428
