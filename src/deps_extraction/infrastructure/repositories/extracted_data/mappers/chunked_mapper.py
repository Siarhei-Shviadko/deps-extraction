from copy import deepcopy
from typing import Any, Optional

from deps_extracted_data.model.extracted_data import (
    EntityId,
    ExtractedField,
    FieldData,
    GenericList,
    Table,
    TableCell,
    TableCellCoordinates,
)
from deps_extracted_data.serializers.base import (
    SerializedTableCell,
    SerializedTableCellCoordinates,
)
from deps_extracted_data.serializers.v2 import (
    TableChunkResponse,
    TableFieldChunk,
    TableFieldChunkMeta,
)
from sqlalchemy.engine import RowMapping

from deps_extraction.domain.dtos import ExtractedDataPaginationParamsObject
from deps_extraction.domain.exceptions import ChunkedExtractedDataError
from deps_extraction.infrastructure.repositories.extracted_data.types import (
    ListOfDictsType,
)

from .bbox_coordinates_mappers import build_source_bbox_coordinates_from_dict
from .table_coordinates_mappers import SourceTableCoordinatesMapper
from .text_coordinates_mappers import SourceTextCoordinatesMapper


class ChunkedMapper:
    @classmethod
    def build_extracted_data_field_chunk(
        cls,
        chunk_data: list[RowMapping],
        edata_field: ExtractedField,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableChunkResponse:
        field_data = cls.get_field_data(edata_field, pagination_params)
        if isinstance(field_data, Table):
            return TableChunkResponse(
                meta=cls.build_chunk_meta(field_data, pagination_params),
                data=cls.build_extracted_data_table_field_chunk_data(chunk_data, pagination_params),
            )

        raise ChunkedExtractedDataError("Chunked extracted-data can be build only with Table field data.")

    @classmethod
    def build_chunk_meta(
        cls,
        field_data: Table,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableFieldChunkMeta:
        return TableFieldChunkMeta(
            rows_chunk=pagination_params.rows_chunk,
            list_index=field_data.meta.list_index,
            chunks_total=field_data.meta.chunks_total,
            rows_total=field_data.meta.rows_total,
        )

    @classmethod
    def build_extracted_data_table_field_chunk_data(  # noqa: WPS:231
        cls,
        field_data_dicts: list[dict[str, Any]],
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableFieldChunk:
        cells = []
        if field_data_dicts:
            cell_list = (
                list(filter(lambda x: int(x["index"].split(".")[0]) == pagination_params.list_index, field_data_dicts))
                if pagination_params.list_index is not None
                else field_data_dicts
            )
            for sorted_cell in cls.sort_cell_list(cell_list):
                if sorted_cell["confidence"] is not None:
                    cell = TableCell(
                        value=sorted_cell["value"],
                        confidence=float(sorted_cell["confidence"]),
                        table_cell_coordinates=ChunkedMapper.build_chunk_table_cell_coordinates(
                            sorted_cell["table_cell_coordinates"],
                            pagination_params,
                        ),
                        id_=EntityId(sorted_cell["id"]),
                    )
                else:
                    cell = TableCell(
                        value=sorted_cell["value"],
                        table_cell_coordinates=ChunkedMapper.build_chunk_table_cell_coordinates(
                            sorted_cell["coordinates"],
                            pagination_params,
                        ),
                        id_=EntityId(sorted_cell["id"]),
                    )
                source_table_coordinates = SourceTableCoordinatesMapper.from_dict(
                    sorted_cell["source_table_coordinates"],
                )
                source_bbox_coordinates = build_source_bbox_coordinates_from_dict(
                    sorted_cell["source_bbox_coordinates"],
                )
                source_text_coordinates = SourceTextCoordinatesMapper.from_dict(sorted_cell["source_text_coordinates"])
                if source_table_coordinates is not None:
                    cell.source_table_coordinates = source_table_coordinates
                elif source_bbox_coordinates is not None:
                    cell.source_bbox_coordinates = source_bbox_coordinates

                elif source_text_coordinates is not None:
                    cell.source_text_coordinates = source_text_coordinates
                else:
                    raise ChunkedExtractedDataError(
                        "Can't build chunked extract-data without one of source coordinates.",
                    )
                cells.append(cell)
        return TableFieldChunk(cells=[SerializedTableCell.from_model(cell) for cell in cells])

    @classmethod
    def sort_cell_list(cls, field_data_dicts: ListOfDictsType) -> ListOfDictsType:
        cell_number_index = cls.get_cell_order_number_index(field_data_dicts)
        if cell_number_index is None:
            return field_data_dicts
        return sorted(field_data_dicts, key=lambda x: x["index"].split(".")[cell_number_index])

    @classmethod
    def get_cell_order_number_index(cls, field_data_dicts: ListOfDictsType) -> Optional[int]:
        index_item_list = cls.get_cell_index_item_list(field_data_dicts)
        if index_item_list is None or "cell" not in index_item_list:
            return None
        cell_anchor_index = index_item_list.index("cell")
        return cell_anchor_index + 1

    @classmethod
    def get_cell_index_item_list(cls, field_data_dicts: ListOfDictsType) -> Optional[list[str]]:
        if field_data_dicts[0]["index"] is None:
            return None
        return field_data_dicts[0]["index"].split(".")

    @classmethod
    def get_field_data(
        cls,
        edata_field: ExtractedField,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> Table:
        if isinstance(edata_field.data, GenericList):
            if pagination_params.list_index is None:
                raise ChunkedExtractedDataError(
                    "Can't build chunked extract-data for list without list_index in pagination params.",
                )
            field_data_element = edata_field.data.elements[pagination_params.list_index]
            if isinstance(field_data_element, Table):
                return field_data_element
        if isinstance(edata_field.data, Table):
            return edata_field.data
        raise ChunkedExtractedDataError(f"Can't build chunked extract-data for {type(edata_field.data)} field type.")

    @classmethod
    def check_field_chunk_data_integrity(cls, field_chunk: TableChunkResponse, field_data: FieldData) -> bool:
        if isinstance(field_data, Table):
            return cls.check_table_field_chunk_data_integrity(field_chunk, field_data)
        raise ChunkedExtractedDataError(f"Can't build chunked data for {type(field_data)}")

    @classmethod
    def check_table_field_chunk_data_integrity(cls, field_chunk: TableChunkResponse, field_data: Table) -> bool:
        chunk_first_row_with_merged_cells_count = sum(
            [c.table_cell_coordinates.column_span for c in field_chunk.data.cells if c.table_cell_coordinates.row == 0],
        )
        return chunk_first_row_with_merged_cells_count == len(field_data.columns)

    @classmethod
    def build_restored_integrity_chunk(
        cls,
        field_chunk: TableChunkResponse,
        field_extra_chunk: TableChunkResponse,
        field_data: FieldData,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableChunkResponse:
        if isinstance(field_chunk, TableChunkResponse):
            return cls.build_restored_integrity_table_chunk(
                field_chunk,
                field_extra_chunk,
                field_data,
                pagination_params,
            )
        raise ChunkedExtractedDataError(f"Can't restore chunk integrity for type {type(field_chunk)} field chunk.")

    @classmethod
    def build_restored_integrity_table_chunk(
        cls,
        field_chunk: TableChunkResponse,
        field_extra_chunk: TableChunkResponse,
        field_data: FieldData,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableChunkResponse:
        cols_count = len(field_data.columns)
        undef_cols = cls.get_undefined_cols(field_chunk.data.cells, cols_count)
        merged_cells = cls.get_merged_cells(field_extra_chunk.data.cells)
        first_row_colspan_count = cls.get_colspan_count(field_chunk.data.cells)
        undef_cols_index = 0
        for mc in merged_cells:
            (restored_cells, undef_cols_index, first_row_colspan_count) = cls.get_restored_cells_by_merged_cell(
                merged_cell=mc,
                undef_cols=undef_cols,
                undef_cols_index=undef_cols_index,
                first_row_colspan_count=first_row_colspan_count,
                cols_count=cols_count,
                pagination_params=pagination_params,
            )
            field_chunk.data.cells.extend(restored_cells)
            if first_row_colspan_count == cols_count:
                break
        return field_chunk

    @classmethod
    def get_undefined_cols(
        cls,
        cells: list[SerializedTableCell],
        cols_count: int,
    ) -> list[int]:
        undefined_cols = []
        sorted_cells = sorted(
            filter(lambda x: x.table_cell_coordinates.row == 0, cells),
            key=lambda x: x.table_cell_coordinates.column,
        )
        cur_col_val = 0
        sorted_cell_i = 0
        while cur_col_val < cols_count:
            if (  # noqa: WPS337
                sorted_cell_i < len(sorted_cells)
                and cur_col_val == sorted_cells[sorted_cell_i].table_cell_coordinates.column
            ):
                cur_col_val += sorted_cells[sorted_cell_i].table_cell_coordinates.column_span
                sorted_cell_i += 1
            else:
                undefined_cols.append(cur_col_val)
                cur_col_val += 1
        return undefined_cols

    @classmethod
    def get_merged_cells(cls, cells: list[SerializedTableCell]) -> list[SerializedTableCell]:
        return sorted(
            filter(
                lambda x: x.table_cell_coordinates.column_span > 1 or x.table_cell_coordinates.row_span > 1,
                cells,
            ),
            key=lambda x: (x.table_cell_coordinates.row, x.table_cell_coordinates.column),
            reverse=True,
        )

    @classmethod
    def get_colspan_count(cls, cells: list[SerializedTableCell]) -> int:
        return sum([c.table_cell_coordinates.column_span for c in cells if c.table_cell_coordinates.row == 0])

    @classmethod
    def get_restored_cells_by_merged_cell(
        cls,
        merged_cell: SerializedTableCell,
        undef_cols: list[int],
        undef_cols_index: int,
        first_row_colspan_count: int,
        cols_count: int,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> tuple[list[SerializedTableCell], int, int]:
        cells = []
        temp_undef_cols_index = undef_cols_index
        row = pagination_params.left_row_index
        while temp_undef_cols_index < len(undef_cols) and first_row_colspan_count != cols_count:
            col = undef_cols[undef_cols_index]
            if cls.check_cell_belongs_to_merged_cells(row, col, merged_cell):
                cell = cls.build_interfered_merged_cell(merged_cell, col, row, pagination_params)
                cells.append(cell)
                undef_cols_index += 1
                first_row_colspan_count += cell.table_cell_coordinates.column_span
            temp_undef_cols_index += 1
        return cells, undef_cols_index, first_row_colspan_count

    @classmethod
    def check_cell_belongs_to_merged_cells(cls, row: int, col: int, mc: SerializedTableCell) -> bool:
        row_range, col_range = cls.get_merged_cell_ranges(mc)
        return row_range[0] <= row <= row_range[1] and col_range[0] <= col <= col_range[1]  # noqa: WPS221

    @classmethod
    def get_merged_cell_ranges(cls, mc: SerializedTableCell) -> tuple[tuple[int, int], tuple[int, int]]:
        row_range = (
            mc.table_cell_coordinates.row,
            mc.table_cell_coordinates.row + mc.table_cell_coordinates.row_span - 1,
        )
        col_range = (
            mc.table_cell_coordinates.column,
            mc.table_cell_coordinates.column + mc.table_cell_coordinates.column_span - 1,
        )
        return row_range, col_range

    @classmethod
    def build_interfered_merged_cell(
        cls,
        merged_cell: SerializedTableCell,
        col: int,
        row: int,
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> SerializedTableCell:
        merged_cell = deepcopy(merged_cell)
        row_range, col_range = cls.get_merged_cell_ranges(merged_cell)
        merged_cell.table_cell_coordinates = SerializedTableCellCoordinates(
            column=col,
            row=row - pagination_params.left_row_index,
            column_span=col_range[1] - col + 1,
            row_span=row_range[1] - row + 1,
        )
        merged_cell.id = merged_cell.id
        return merged_cell

    @classmethod
    def build_chunk_table_cell_coordinates(
        cls,
        coordinates: dict[str, Any],
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> TableCellCoordinates:
        return TableCellCoordinates(
            row=(
                coordinates["row"]
                if pagination_params.original_data
                else coordinates["row"] - pagination_params.left_row_index
            ),
            column=coordinates["column"],
            row_span=(
                coordinates["row_span"]
                if pagination_params.original_data
                else min(coordinates["row_span"], pagination_params.rows_per_chunk)
            ),
            column_span=coordinates["column_span"],
        )
