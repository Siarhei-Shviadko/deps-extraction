from typing import Any, Optional

from deps_extracted_data import ExtractedData
from sqlalchemy import and_, delete, insert, or_, select, subquery
from sqlalchemy.engine import RowProxy
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql import Select

from deps_extraction.api.constants import PaginationFieldTypeEnum
from deps_extraction.domain.dtos import (
    ExtractedDataFilterObject,
    ExtractedDataListFilterObject,
)
from deps_extraction.domain.exceptions import ExtractedDataNotFound
from deps_extraction.domain.interfaces import IExtractedDataRepository, ITenantDAO
from deps_extraction.extras.datasource import Database
from deps_extraction.infrastructure.repositories.extracted_data.mappers import (
    ExtractedDataMapper,
    PaginatedFieldMapper,
)
from deps_extraction.infrastructure.tables import (
    extracted_field_table,
    groups_table,
    tenant_documents_table,
)

__all__ = ["ExtractedDataRepository"]


class ExtractedDataRepository(IExtractedDataRepository):  # noqa: WPS214
    def __init__(
        self,
        database: Database,
        tenant_dao: ITenantDAO,
    ):
        self._db = database
        self._tenant_dao = tenant_dao

    def save(self, extracted_data: ExtractedData) -> ExtractedData:
        with self._db.connection() as conn:
            if self.extracted_data_exists(conn, extracted_data.document_id):
                self._delete_old_extracted_data(conn, extracted_data)

            edata_dict = ExtractedDataMapper.to_dicts(extracted_data)
            if fields_dict := edata_dict["fields"]:
                q = insert(extracted_field_table)
                conn.execute(q, fields_dict)
                self._save_groups(conn, edata_dict["groups"])
                self._tenant_dao.add_to_tenant(conn, extracted_data.document_id)
        return extracted_data

    def find(self, document_id: int) -> ExtractedData:
        with self._db.connection() as conn:
            query = self._get_query_for_tenant(filtering=ExtractedDataFilterObject(document_id=document_id))
            res = conn.execute(query).fetchall()
            if not res:
                raise ExtractedDataNotFound(document_id)
            return ExtractedDataMapper().from_dicts(res)

    def find_by_filter(self, filtering: ExtractedDataFilterObject) -> ExtractedData:
        with self._db.connection() as conn:
            query = self._get_query_for_tenant(filtering)
            res = conn.execute(query).fetchall()
            if not res:
                raise ExtractedDataNotFound(filtering.document_id)
            return ExtractedDataMapper().from_dicts(res)

    def delete(self, document_id: int) -> None:
        with self._db.connection() as conn:
            if self.extracted_data_exists(conn, document_id):
                self._tenant_dao.check_access(conn, document_id)
                conn.execute(extracted_field_table.delete().where(extracted_field_table.c.document_id == document_id))
                conn.execute(groups_table.delete().where(groups_table.c.document_id == document_id))
                self._tenant_dao.remove_from_tenant(conn, document_id)

    def find_list_by_filter(self, filtering: ExtractedDataListFilterObject) -> list[ExtractedData]:
        with self._db.connection() as conn:
            self._tenant_dao.patch_filter(conn, filtering)
            query = self._get_list_query(extracted_field_table, limit=filtering.limit, offset=filtering.offset)
            query = self._apply_list_filtering(query, filtering)
            query = query.order_by(
                extracted_field_table.c.document_id,
                extracted_field_table.c.field_code,
            )

            res = conn.execute(query).fetchall()

        if not res:
            return []

        return ExtractedDataMapper().edata_list_from_dicts(res)

    def extracted_data_exists(self, conn: Connection, document_id: int) -> RowProxy:
        query = select([extracted_field_table.c.document_id])
        query = self._apply_filtering(query, ExtractedDataFilterObject(document_id=document_id))
        return conn.execute(query).fetchone()

    def find_with_internal_pagination(self, document_id: int, rows_per_chunk: int) -> ExtractedData:
        edata = ExtractedData(document_id)
        with self._db.connection() as conn:
            paginated_edata = self._get_paginated_extracted_data(conn, document_id)
            paginated_fields, paginated_groups = (
                (
                    PaginatedFieldMapper.build_paginated_field_types(
                        fields=paginated_edata.fields,
                        per_chunk=rows_per_chunk,
                    ),
                    paginated_edata.groups,
                )
                if paginated_edata
                else ([], [])
            )

            non_paginated_edata = self._get_non_paginated_extracted_data(
                conn,
                document_id,
                [field.field_code for field in paginated_fields],
            )
            non_paginated_fields, non_paginated_groups = (
                (non_paginated_edata.fields, non_paginated_edata.groups) if non_paginated_edata else ([], [])
            )
        if paginated_edata is None and non_paginated_edata is None:
            raise ExtractedDataNotFound(document_id)

        edata.add_extracted_fields(non_paginated_fields + paginated_fields)
        edata.add_groups(paginated_groups + non_paginated_groups)
        return edata

    def _get_non_paginated_extracted_data(
        self,
        conn: Connection,
        document_id: int,
        field_codes: list[str],
    ) -> Optional[ExtractedData]:
        non_paginated_query = self._get_query_for_tenant(
            filtering=ExtractedDataFilterObject(
                document_id=document_id,
                paginated_field_codes=field_codes,
            ),
        )
        non_paginated_fields_res = conn.execute(non_paginated_query).fetchall()

        return ExtractedDataMapper().from_dicts(non_paginated_fields_res) if non_paginated_fields_res else None

    def _get_paginated_extracted_data(self, conn: Connection, document_id: int) -> Optional[ExtractedData]:
        paginated_query = self._get_query_for_tenant(
            filtering=ExtractedDataFilterObject(
                document_id=document_id,
                indexes=[PaginationFieldTypeEnum.TABLE],
            ),
        )
        paginated_res = conn.execute(paginated_query).fetchall()
        return ExtractedDataMapper().from_dicts(paginated_res) if paginated_res else None

    def _delete_old_extracted_data(self, conn: Connection, extracted_data: ExtractedData) -> None:
        self._tenant_dao.check_access(conn, extracted_data.document_id)
        conn.execute(
            delete(extracted_field_table).where(
                extracted_field_table.c.document_id == extracted_data.document_id,
            ),
        )
        conn.execute(delete(groups_table).where(groups_table.c.document_id == extracted_data.document_id))
        self._tenant_dao.remove_from_tenant(conn, extracted_data.document_id)

    def _save_groups(self, conn: Connection, groups: dict[str, Any]) -> None:
        query = insert(groups_table)
        conn.execute(query, groups)

    @staticmethod
    def _get_list_query(requested_select, limit: Optional[int] = None, offset: Optional[int] = None):
        distinct_document_ids_select = subquery(
            "distinct_document_ids",
            [extracted_field_table.c.document_id],
            distinct=True,
            order_by=extracted_field_table.c.document_id,
            limit=limit,
            offset=offset,
        )

        return (
            select([requested_select, groups_table.c.groups])
            .select_from(
                extracted_field_table.join(
                    groups_table,
                    groups_table.c.document_id == extracted_field_table.c.document_id,
                ),
            )
            .where(extracted_field_table.c.document_id.in_(distinct_document_ids_select))
        )

    def _get_query(self, filtering: ExtractedDataFilterObject) -> Select:
        query = select([extracted_field_table])
        query = self._apply_filtering(query, filtering)
        return query.order_by(extracted_field_table.c.field_code)

    def _get_query_for_tenant(self, filtering: ExtractedDataFilterObject) -> Select:
        joined = extracted_field_table.join(
            tenant_documents_table,
            tenant_documents_table.c.document_id == extracted_field_table.c.document_id,
            isouter=True,
        ).join(
            groups_table,
            groups_table.c.document_id == extracted_field_table.c.document_id,
            isouter=True,
        )
        query = (
            select([extracted_field_table, groups_table.c.groups])
            .select_from(joined)
            .where(self._tenant_dao.current_tenant == tenant_documents_table.c.tenant_id)
        )
        query = self._apply_filtering(query, filtering)

        return query.order_by(extracted_field_table.c.field_code)

    @staticmethod
    def _apply_filtering(query, filtering: ExtractedDataFilterObject) -> Select:
        if filtering.document_id is not None:
            query = query.where(extracted_field_table.c.document_id == filtering.document_id)
        if filtering.field_codes is not None:
            query = query.where(extracted_field_table.c.field_code.in_(filtering.field_codes))
        if filtering.field_types is not None:
            fields_like_expression = [
                extracted_field_table.c.field_type.like(f"{type_}") for type_ in filtering.field_types
            ]
            query = query.where(or_(*fields_like_expression))
        if filtering.paginated_field_codes is not None:
            query = query.where(and_(extracted_field_table.c.field_code.notin_(filtering.paginated_field_codes)))
        if filtering.indexes is not None:
            fields_like_expression = [extracted_field_table.c.index.like(f"%{ind}") for ind in filtering.indexes]
            query = query.where(or_(*fields_like_expression))
        return query

    @staticmethod
    def _apply_list_filtering(query, filtering: ExtractedDataListFilterObject) -> Select:
        if filtering.document_ids is not None:
            query = query.where(extracted_field_table.c.document_id.in_(filtering.document_ids))

        return query
