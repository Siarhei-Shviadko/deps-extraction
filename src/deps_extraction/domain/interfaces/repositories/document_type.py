from abc import ABC, abstractmethod
from typing import ContextManager, Optional

from sqlalchemy.engine.base import Connection

from ...model import DocumentType

__all__ = ["IDocumentTypeRepository"]


class IDocumentTypeRepository(ABC):
    @abstractmethod
    def get(self, document_type_id: str) -> Optional[DocumentType]:
        pass

    @abstractmethod
    def find_by_name_for_tenant(self, document_type_name: str, tenant_id: str) -> Optional[DocumentType]:
        pass

    @abstractmethod
    def find_by_id_for_tenant(self, document_type_id: str, tenant_id: str) -> DocumentType:
        pass

    @abstractmethod
    def find_by_tenant(self, tenant_id: str) -> list[DocumentType]:
        pass

    @abstractmethod
    def save(self, document_type: DocumentType) -> None:
        pass

    @abstractmethod
    def save_new(self, document_type: DocumentType) -> None:
        pass

    @abstractmethod
    def save_all(self, document_types: list[DocumentType]) -> None:
        pass

    @abstractmethod
    def save_new_all(self, document_types: list[DocumentType]) -> None:
        pass

    @abstractmethod
    def delete(self, document_type: DocumentType) -> None:
        pass

    @abstractmethod
    def find_all(self) -> list[DocumentType]:
        pass

    @abstractmethod
    def repeatable_read(self) -> ContextManager[Connection]:
        pass
