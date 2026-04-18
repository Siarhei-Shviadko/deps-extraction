from typing import Iterable, Optional

from deps_extracted_data.model.extracted_data import (
    ExtractedField,
    FieldData,
    GenericList,
    Table,
    TableMeta,
    TableRow,
)

__all__ = ["PaginatedFieldMapper"]
FIRST_ELEMENT = 0


class PaginatedFieldMapper:
    @classmethod
    def build_paginated_field_types(cls, fields: list[ExtractedField], per_chunk: int) -> list[ExtractedField]:
        for field in filter(lambda f: cls.check_table_data_is_paginated_type(f.data), fields):  # noqa: WPS426
            cls.add_pagination_info_to_field(field.data, per_chunk)
        return fields

    @classmethod
    def add_pagination_info_to_field(
        cls,
        field_data: FieldData,
        per_chunk: int,
        index: Optional[int] = None,
    ) -> FieldData:
        if isinstance(field_data, GenericList):
            for ind, data in enumerate(field_data.elements):
                cls.add_pagination_info_to_field(data, per_chunk, ind)
            return field_data
        if isinstance(field_data, Table):
            field_data.meta = cls.build_table_meta(field_data, per_chunk, index)
            field_data.paginated_rows = list(cls.split_table_rows_to_chunks(field_data.rows, per_chunk))
        return field_data

    @classmethod
    def build_table_meta(cls, field_data: Table, per_chunk: int, index: Optional[int] = None) -> TableMeta:
        rows_total = len(field_data.rows)
        return TableMeta(
            chunks_total=(rows_total // per_chunk) + (1 if rows_total % per_chunk else 0),  # noqa: WPS509
            rows_total=rows_total,
            list_index=index,
        )

    @classmethod
    def split_table_rows_to_chunks(cls, rows: list[TableRow], per_chunk: int) -> Iterable[list[TableRow]]:
        def _get_y(r, s_r, y_diff):  # noqa: WPS430
            if y_diff != 0:
                return (r.y - s_r.y) / y_diff
            return r.y

        for chunk_start_index in range(0, len(rows), per_chunk):
            chunk_rows = rows[chunk_start_index : chunk_start_index + per_chunk]  # noqa: E203
            start_row = chunk_rows[0]
            if chunk_start_index + per_chunk < len(rows):
                chunk_rows_y_diff = rows[chunk_start_index + per_chunk].y - start_row.y
            else:
                chunk_rows_y_diff = 1 - start_row.y
            yield [TableRow(y=_get_y(row, start_row, chunk_rows_y_diff)) for row in chunk_rows]

    @classmethod
    def check_table_data_is_paginated_type(cls, field_data: FieldData) -> bool:
        return isinstance(
            field_data.elements[FIRST_ELEMENT] if isinstance(field_data, GenericList) else field_data,
            Table,
        )
