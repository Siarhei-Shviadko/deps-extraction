import logging

from sqlalchemy import and_, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine.base import Connection

from deps_extraction.domain.dtos import ExtractedDataListFilterObject
from deps_extraction.domain.exceptions import AuthError, ExtractedDataForbidden
from deps_extraction.domain.interfaces import ITenantDAO
from deps_extraction.infrastructure.tables import tenant_documents_table

from .context_vars import user


class TenantDAO(ITenantDAO):
    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def current_tenant(self) -> str:
        user_credentials = user.get(None)
        if user_credentials is None or user_credentials.get("organisation") is None:
            self._logger.error(
                f"User credentials doens't provided or application can't get user tenant.{user_credentials}",
            )
            raise AuthError("User credentials doesn't provided.")
        return user_credentials["organisation"]

    def add_to_tenant(self, conn: Connection, document_id: int) -> None:
        conn.execute(
            insert(tenant_documents_table)
            .values(tenant_id=self.current_tenant, document_id=document_id)
            .on_conflict_do_nothing(),
        )
        self._logger.debug(
            f"Add_to_tenant completed with document_id: {document_id} and tenant_id {self.current_tenant}",
        )

    def remove_from_tenant(self, conn: Connection, document_id: int) -> None:
        conn.execute(
            delete(tenant_documents_table).where(
                and_(
                    tenant_documents_table.c.tenant_id == self.current_tenant,
                    tenant_documents_table.c.document_id == document_id,
                ),
            ),
        )
        self._logger.debug(
            f"Remove_from_tenant completed with document_id: {document_id} and tenant_id {self.current_tenant}",
        )

    def get_document_ids(self, conn: Connection) -> list[int]:
        res = conn.execute(
            select([tenant_documents_table.c.document_id])
            .where(tenant_documents_table.c.tenant_id == self.current_tenant)
            .select_from(tenant_documents_table),
        )

        return [int(row[0]) for row in res.fetchall()]

    def check_access(self, conn: Connection, document_id: int) -> None:
        query = select([tenant_documents_table]).where(
            and_(
                tenant_documents_table.c.tenant_id == self.current_tenant,
                tenant_documents_table.c.document_id == document_id,
            ),
        )
        if not conn.execute(query).fetchone():
            self._logger.debug(
                f"Check_access failed for document_id: {document_id} and tenant_id: {self.current_tenant}.",
            )
            raise ExtractedDataForbidden(document_id)
        self._logger.debug(
            f"Check_access successful for document_id: {document_id} and tenant_id: {self.current_tenant}",
        )

    def patch_filter(self, conn: Connection, filtering: ExtractedDataListFilterObject) -> None:
        document_ids = self.get_document_ids(conn)
        if filtering.document_ids:
            filtering.document_ids = list(set(filtering.document_ids).intersection(set(document_ids)))
            return
        filtering.document_ids = document_ids
