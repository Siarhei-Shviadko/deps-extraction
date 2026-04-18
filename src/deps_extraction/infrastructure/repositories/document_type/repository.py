import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import Column, and_, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine.base import Connection

from deps_extraction.domain.exceptions import DocumentTypeNotFound
from deps_extraction.domain.interfaces.repositories import IDocumentTypeRepository
from deps_extraction.domain.model import DocumentType
from deps_extraction.extras.datasource import Database

from ...tables import document_type_table
from .mappers import DocumentTypeMapper

__all__ = ["DocumentTypeRepository"]


class DocumentTypeRepository(IDocumentTypeRepository):
    def __init__(self, database: Database):
        self.db = database

        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def document_type_columns(self) -> list[Column]:
        return [
            document_type_table.c.id,
            document_type_table.c.tenant_id,
            document_type_table.c.name,
            document_type_table.c.extraction_type,
            document_type_table.c.extractors,
        ]

    def get(self, document_type_id: str) -> Optional[DocumentType]:
        query = select(self.document_type_columns).where(document_type_table.c.id == document_type_id)

        with self.db.connection() as conn:
            rows = conn.execute(query).fetchone()

        if rows:
            return DocumentTypeMapper.from_dict(rows)

        return None

    def find_by_name_for_tenant(self, document_type_name: str, tenant_id: str) -> Optional[DocumentType]:
        query = select(self.document_type_columns).where(
            and_(
                document_type_table.c.name == document_type_name,
                document_type_table.c.tenant_id == tenant_id,
            ),
        )

        with self.db.connection() as conn:
            rows = conn.execute(query).fetchone()

        if rows:
            return DocumentTypeMapper.from_dict(rows)

        return None

    def find_by_id_for_tenant(self, document_type_id: str, tenant_id: str) -> DocumentType:
        query = select(self.document_type_columns).where(
            and_(
                document_type_table.c.tenant_id == tenant_id,
                document_type_table.c.id == document_type_id,
            ),
        )

        with self.db.connection() as conn:
            rows = conn.execute(query).fetchone()

        if rows:
            return DocumentTypeMapper.from_dict(rows)

        raise DocumentTypeNotFound(document_type_id)

    def find_by_tenant(self, tenant_id: str) -> list[DocumentType]:
        query = select(self.document_type_columns).where(document_type_table.c.tenant_id == tenant_id)

        with self.db.connection() as conn:
            rows = conn.execute(query).fetchall()

        return [DocumentTypeMapper.from_dict(row) for row in rows]

    def save(self, document_type: DocumentType) -> None:
        raw_document_type = DocumentTypeMapper.to_dict(document_type)

        insert_query = insert(document_type_table).values(**raw_document_type)
        save_query = insert_query.on_conflict_do_update(
            index_elements=[document_type_table.c.id, document_type_table.c.tenant_id],
            set_=dict(insert_query.excluded),
        )

        with self.db.connection() as conn:
            conn.execute(save_query)

    def save_new(self, document_type: DocumentType) -> None:
        save_query = insert(document_type_table).on_conflict_do_nothing()

        with self.db.connection() as conn:
            conn.execute(save_query, DocumentTypeMapper.to_dict(document_type))

    def save_all(self, document_types: list[DocumentType]) -> None:
        if not document_types:
            return

        raw_document_types = [DocumentTypeMapper.to_dict(doc_type) for doc_type in document_types]

        insert_query = insert(document_type_table)
        save_query = insert_query.on_conflict_do_update(
            index_elements=[document_type_table.c.id, document_type_table.c.tenant_id],
            set_=dict(insert_query.excluded),
        )

        with self.db.connection() as conn:
            conn.execute(save_query, raw_document_types)

    def save_new_all(self, document_types: list[DocumentType]) -> None:
        if not document_types:
            return

        raw_document_types = [DocumentTypeMapper.to_dict(doc_type) for doc_type in document_types]

        save_query = insert(document_type_table).on_conflict_do_nothing()

        with self.db.connection() as conn:
            conn.execute(save_query, raw_document_types)

    def delete(self, document_type: DocumentType) -> None:
        query = delete(document_type_table).where(
            and_(
                document_type_table.c.tenant_id == document_type.tenant_id(),
                document_type_table.c.id == document_type.id(),
            ),
        )

        with self.db.connection() as conn:
            conn.execute(query)

    def find_all(self) -> list[DocumentType]:
        query = select(self.document_type_columns)

        with self.db.connection() as conn:
            rows = conn.execute(query).fetchall()

        return [DocumentTypeMapper.from_dict(row) for row in rows]

    @contextmanager
    def repeatable_read(self) -> Generator[Connection, None, None]:
        with self.db.connection(isolation_level="REPEATABLE READ") as conn:
            yield conn
