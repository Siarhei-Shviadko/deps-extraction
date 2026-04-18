from typing import Optional

from deps_extracted_data.model.extracted_data import ExtractedField, Table
from deps_extracted_data.serializers.v2 import TableChunkResponse
from sqlalchemy import and_, bindparam, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine.base import Connection

from deps_extraction.api.constants import PaginationFieldTypeEnum
from deps_extraction.domain.dtos import (
    ExtractedDataFilterObject,
    ExtractedDataPaginationParamsObject,
    TableFieldRowsRange,
)
from deps_extraction.domain.exceptions import (
    ChunkedExtractedDataError,
    ExtractedDataNotFound,
)
from deps_extraction.domain.interfaces import ITenantDAO
from deps_extraction.extras.datasource import Database
from deps_extraction.infrastructure.repositories.extracted_data.types import (
    CommonDictType,
    ListOfDictsType,
)
from deps_extraction.infrastructure.tables import extracted_field_table

from .mappers import ExtractedFieldMapper, PaginatedFieldMapper
from .mappers.chunked_mapper import ChunkedMapper

__all__ = ["ChunkedExtractedDataRepository"]

PARTIAL_UPDATE_COLUMNS = ("value", "confidence", "_id", "source_bbox_coordinates")


class ChunkedExtractedDataRepository:
    def __init__(self, database: Database, tenant_dao: ITenantDAO):
        self._db = database
        self._tenant_dao = tenant_dao

    def put_table_info(self, info: CommonDictType) -> None:
        q = insert(extracted_field_table)
        stmt = q.on_conflict_do_update(
            index_elements=[
                extracted_field_table.c.index,
                extracted_field_table.c.document_id,
                extracted_field_table.c.field_code,
            ],
            index_where=and_(
                extracted_field_table.c.index.like("%table"),
                extracted_field_table.c.document_id == info["document_id"],
                extracted_field_table.c.field_code == info["field_code"],
            ),
            set_={
                "meta": info["meta"],
                "source_bbox_coordinates": info["source_bbox_coordinates"],
                "source_table_coordinates": info["source_table_coordinates"],
            },
        )

        with self._db.connection() as conn:
            conn.execute(stmt, info)
            self._tenant_dao.add_to_tenant(conn, info["document_id"])

    def put_table_chunked_data(self, data: ListOfDictsType, document_id: int) -> None:
        q = insert(extracted_field_table)
        stmt = q.on_conflict_do_update(
            index_elements=[
                extracted_field_table.c.index,
                extracted_field_table.c.document_id,
                extracted_field_table.c.field_code,
            ],
            index_where=and_(
                extracted_field_table.c.index == q.excluded.index,
                extracted_field_table.c.document_id == q.excluded.document_id,
                extracted_field_table.c.field_code == q.excluded.field_code,
            ),
            set_={
                "value": q.excluded.value,
                "confidence": q.excluded.confidence,
            },
        )

        with self._db.connection() as conn:
            conn.execute(stmt, data)
            self._tenant_dao.add_to_tenant(conn, document_id)

    def get_field_chunk(
        self,
        document_id: int,
        field_code: str,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableChunkResponse:
        with self._db.connection() as conn:
            self._tenant_dao.check_access(conn, document_id)
            edata_field = self._get_field_with_internal_pagination(
                conn,
                document_id,
                field_code,
                pagination_params.rows_per_chunk,
            )

            return self._get_field_chunk(conn, document_id, field_code, edata_field, pagination_params)

    def batch_partial_update_field(self, document_id: int, field_code: str, data: ListOfDictsType) -> None:
        if data:
            bindparam_fields = {col: bindparam(col) for col in PARTIAL_UPDATE_COLUMNS if col != "_id"}
            update_query = (
                update(extracted_field_table)
                .where(
                    and_(
                        extracted_field_table.c.document_id == document_id,
                        extracted_field_table.c.field_code == field_code,
                        extracted_field_table.c.id == bindparam("_id"),
                    ),
                )
                .values(bindparam_fields)
            )

            with self._db.connection() as conn:
                self._tenant_dao.check_access(conn, document_id)
                conn.execute(update_query, [{k: cell[k] for k in cell if k in PARTIAL_UPDATE_COLUMNS} for cell in data])

    def _get_field_with_internal_pagination(
        self,
        connection: Connection,
        document_id: int,
        field_code: str,
        per_chunk: int,
    ) -> ExtractedField:
        query = select([extracted_field_table])
        query = self._apply_filtering(
            query,
            ExtractedDataFilterObject(
                document_id,
                field_codes=[field_code],
                indexes=[PaginationFieldTypeEnum.TABLE],
            ),
        )
        res = connection.execute(query).fetchall()
        if res:
            edata_field = ExtractedFieldMapper.from_dicts(res)
            PaginatedFieldMapper.add_pagination_info_to_field(edata_field.data, per_chunk)
            return edata_field
        raise ExtractedDataNotFound(document_id)

    def _get_field_chunk(
        self,
        connection: Connection,
        document_id: int,
        field_code: str,
        edata_field_entity: ExtractedField,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableChunkResponse:
        field_chunk = self._get_field_chunk_without_integrity(
            connection,
            document_id,
            field_code,
            edata_field_entity,
            pagination_params,
        )
        field_data = ChunkedMapper.get_field_data(edata_field_entity, pagination_params)

        if not ChunkedMapper.check_field_chunk_data_integrity(field_chunk, field_data):
            field_extra_chunk = self._get_extra_chunk(
                connection,
                document_id,
                field_code,
                edata_field_entity,
                pagination_params,
            )
            field_chunk = ChunkedMapper.build_restored_integrity_chunk(
                field_chunk,
                field_extra_chunk,
                field_data,
                pagination_params,
            )

        return field_chunk

    def _get_field_chunk_without_integrity(
        self,
        conn: Connection,
        document_id: int,
        field_code: str,
        edata_field: ExtractedField,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableChunkResponse:
        query = select([extracted_field_table])
        query = self._apply_filtering(
            query,
            filtering=ExtractedDataFilterObject(
                document_id=document_id,
                field_codes=[field_code],
                field_rows_range=self._build_field_rows_range(
                    ChunkedMapper.get_field_data(edata_field, pagination_params),
                    pagination_params,
                ),
            ),
        )
        res = conn.execute(query).fetchall()

        return ChunkedMapper.build_extracted_data_field_chunk(
            chunk_data=res,
            edata_field=edata_field,
            pagination_params=pagination_params,
        )

    def _apply_filtering(self, query, filtering: ExtractedDataFilterObject):
        if filtering.document_id is not None:
            query = query.where(extracted_field_table.c.document_id == filtering.document_id)
        if filtering.field_codes is not None:
            query = query.where(extracted_field_table.c.field_code.in_(filtering.field_codes))
        if filtering.field_types is not None:
            fields_like_expression = [
                extracted_field_table.c.field_type.like(f"%{field}%") for field in filtering.field_types
            ]
            query = query.where(or_(*fields_like_expression))
        if filtering.field_rows_range is not None:
            query = query.where(
                and_(
                    extracted_field_table.c.table_cell_coordinates["row"]
                    .as_integer()
                    .between(filtering.field_rows_range.left, filtering.field_rows_range.right),
                    extracted_field_table.c.index.like("%cell%"),
                ),
            )
        if filtering.indexes is not None:
            indexes_like_expression = [extracted_field_table.c.index.like(f"%{index}%") for index in filtering.indexes]
            query = query.where(or_(*indexes_like_expression))

        return query

    def _build_field_rows_range(
        self,
        field_data: Table,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> Optional[TableFieldRowsRange]:
        left_index, right_index = pagination_params.left_row_index, pagination_params.right_row_index
        if isinstance(field_data, Table):
            return TableFieldRowsRange(left=left_index, right=right_index - 1)
        return None

    def _get_extra_chunk(
        self,
        conn: Connection,
        document_id: int,
        field_code: str,
        edata_field: ExtractedField,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableChunkResponse:
        field_data = ChunkedMapper.get_field_data(edata_field, pagination_params)
        if isinstance(field_data, Table):
            pagination_params = self._build_pagination_params_for_extra_chunk(pagination_params)
            return self._get_field_chunk_without_integrity(
                conn=conn,
                document_id=document_id,
                field_code=field_code,
                edata_field=edata_field,
                pagination_params=ExtractedDataPaginationParamsObject(
                    rows_per_chunk=pagination_params.rows_per_chunk,
                    rows_chunk=pagination_params.rows_chunk,
                    list_index=pagination_params.list_index,
                    original_data=True,
                ),
            )
        raise ChunkedExtractedDataError(f"Can't get extra_chunk for {type(field_data)} field data.")

    @staticmethod
    def _build_pagination_params_for_extra_chunk(
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> ExtractedDataPaginationParamsObject:
        return ExtractedDataPaginationParamsObject(
            rows_per_chunk=pagination_params.left_row_index,
            rows_chunk=1,
            list_index=pagination_params.list_index,
        )
