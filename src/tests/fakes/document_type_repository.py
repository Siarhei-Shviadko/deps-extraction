from contextlib import contextmanager
from copy import deepcopy
from typing import Any, Generator, Optional

from sqlalchemy.engine.base import Connection

from deps_extraction.domain.exceptions import DocumentTypeNotFound
from deps_extraction.domain.interfaces.repositories.document_type import (
    IDocumentTypeRepository,
)
from deps_extraction.domain.model import DocumentType

__all__ = ["FakeDocumentTypeRepository"]


class _FakeDatabase:
    @contextmanager
    def connection(self, *args, **kwargs):
        yield self


class FakeDocumentTypeRepository(IDocumentTypeRepository):
    def __init__(self) -> None:
        self._db: dict[str, Any] = {}
        self.db = _FakeDatabase()

    def get(self, document_type_id: str) -> Optional[DocumentType]:
        return self._db.get(document_type_id)

    def find_by_name_for_tenant(self, document_type_name: str, tenant_id: str) -> Optional[DocumentType]:
        tenant_document_types = self.find_by_tenant(tenant_id)
        return next(
            (document_type for document_type in tenant_document_types if document_type.name == document_type_name), None
        )

    def find_by_id_for_tenant(self, document_type_id: str, tenant_id: str) -> DocumentType:
        document_type = self._db.get(document_type_id)
        if document_type is None or document_type.tenant_id() != tenant_id:
            raise DocumentTypeNotFound(document_type_id)

        return document_type

    def find_by_tenant(self, tenant_id: str) -> list[DocumentType]:
        return [document_type for document_type in self._db.values() if document_type.tenant_id() == tenant_id]

    def save(self, document_type: DocumentType) -> None:
        self._db[document_type.id()] = deepcopy(document_type)

    def save_new(self, document_type: DocumentType) -> None:
        document_type_id = document_type.id()
        if document_type_id not in self._db:
            self._db[document_type_id] = deepcopy(document_type)

    def save_all(self, document_types: list[DocumentType]) -> None:
        for document_type in document_types:
            self.save(document_type)

    def save_new_all(self, document_types: list[DocumentType]) -> None:
        for document_type in document_types:
            self.save_new(document_type)

    def delete(self, document_type: DocumentType) -> None:
        document_type_id = document_type.id()
        saved_document_type = self._db.get(document_type_id)
        if saved_document_type is not None and saved_document_type.tenant_id == document_type.tenant_id:
            self._db.pop(document_type_id)

    def find_all_with_llm_extractors(self) -> list[DocumentType]:
        return [
            document_type
            for document_type in self._db.values()
            if "llm" in [extractor.type for extractor in document_type.extractors.values()]
        ]

    def find_all(self) -> list[DocumentType]:
        return list(self._db.values())

    @contextmanager
    def repeatable_read(self) -> Generator[Connection, None, None]:
        with self.db.connection() as conn:
            yield conn
