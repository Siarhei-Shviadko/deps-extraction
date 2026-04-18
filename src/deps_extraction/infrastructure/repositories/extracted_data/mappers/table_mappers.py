from copy import deepcopy
from typing import Optional, Union

from deps_extracted_data import (
    FieldType,
    Table,
    TableCell,
    TableCellCoordinates,
    TableColumn,
    TableMeta,
    TableRow,
)
from deps_extracted_data.model.extracted_data.data_types import EntityId
from sqlalchemy.engine import RowProxy

from ..types import CommonDictType, ListOfDictsType
from .bbox_coordinates_mappers import (
    build_dict_from_source_bbox_coordinates,
    build_source_bbox_coordinates_from_dict,
)
from .table_coordinates_mappers import SourceTableCoordinatesMapper
from .text_coordinates_mappers import SourceTextCoordinatesMapper
from .utils import build_dict_for_meta_column_from

FIRST_ELEMENT: int = 0

__all__ = ["TableMetaMapper", "TableMapper"]


class TableMetaMapper:
    @staticmethod
    def to_dict(meta: TableMeta) -> CommonDictType:
        meta_dict = {
            "chunks_total": meta.chunks_total,
            "rows_total": meta.rows_total,
        }
        if meta.list_index is not None:
            meta_dict["list_index"] = meta.list_index
        return meta_dict

    @staticmethod
    def from_dict(raw_meta: CommonDictType) -> TableMeta:
        table_meta = TableMeta(
            chunks_total=raw_meta["chunks_total"],
            rows_total=raw_meta["rows_total"],
        )
        if raw_meta.get("list_index"):
            table_meta.list_index = raw_meta["list_index"]
        return table_meta


class TableMapper:
    @staticmethod
    def to_dicts(table: Table, index: Optional[str] = None, alias: Optional[str] = None) -> ListOfDictsType:
        table_dicts = [
            {
                "id": cell.id(),
                "field_type": FieldType.TABLE.value,
                "value": cell.value,
                "confidence": cell.confidence,
                "index": f"{index}.cell.{num}" if index is not None else f"cell.{num}",
                "meta": None,
                "table_cell_coordinates": TableMapper().build_table_cell_coordinates(cell.table_cell_coordinates),
                "source_bbox_coordinates": build_dict_from_source_bbox_coordinates(cell.source_bbox_coordinates),
                "source_table_coordinates": SourceTableCoordinatesMapper.to_dict(cell.source_table_coordinates),
                "source_text_coordinates": SourceTextCoordinatesMapper.to_dict(cell.source_text_coordinates),
            }
            for num, cell in enumerate(table.cells)
        ]

        table_row_dict: CommonDictType = {
            "id": table.id(),
            "field_type": FieldType.TABLE.value,
            "value": None,
            "confidence": None,
            "index": f"{index}.table" if index else "table",
            "table_cell_coordinates": None,
            "meta": build_dict_for_meta_column_from(
                keys=("columns", "rows", "alias"),
                values=([column.x for column in table.columns], [row.y for row in table.rows], alias),
            ),
            "source_bbox_coordinates": build_dict_from_source_bbox_coordinates(table.source_bbox_coordinates),
            "source_table_coordinates": SourceTableCoordinatesMapper.to_dict(table.source_table_coordinates),
            "source_text_coordinates": None,
        }

        table_dicts.append(table_row_dict)

        return table_dicts

    def from_dicts(self, raw_fields: list[Union[RowProxy, CommonDictType]]) -> Table:  # noqa: WPS231
        cells = []
        copied_fields = deepcopy(raw_fields)
        for num, field in enumerate(copied_fields):
            if field["index"] and field["index"].split(".")[-1] == "table":
                table_row = copied_fields.pop(num)
                break
        if copied_fields:
            for sorted_cell in self.sort_cell_list(copied_fields):
                confidence = float(sorted_cell["confidence"]) if sorted_cell["confidence"] is not None else None
                if confidence:
                    cell = TableCell(
                        value=sorted_cell["value"],
                        table_cell_coordinates=TableCellCoordinates(**sorted_cell["table_cell_coordinates"]),
                        confidence=confidence,
                        id_=EntityId(sorted_cell["id"]),
                    )
                else:
                    cell = TableCell(
                        value=sorted_cell["value"],
                        table_cell_coordinates=TableCellCoordinates(**sorted_cell["table_cell_coordinates"]),
                        id_=EntityId(sorted_cell["id"]),
                    )
                source_bbox_coordinates = build_source_bbox_coordinates_from_dict(
                    sorted_cell["source_bbox_coordinates"],
                )
                if source_bbox_coordinates is not None:
                    cell.source_bbox_coordinates = source_bbox_coordinates
                source_table_coordinates = SourceTableCoordinatesMapper.from_dict(
                    sorted_cell["source_table_coordinates"],
                )
                if source_table_coordinates is not None:
                    cell.source_table_coordinates = source_table_coordinates
                source_text_coordinates = SourceTextCoordinatesMapper.from_dict(
                    sorted_cell["source_text_coordinates"],
                )
                if source_text_coordinates is not None:
                    cell.source_text_coordinates = source_text_coordinates
                cells.append(cell)

        field_meta = table_row["meta"]

        table = Table(
            columns=list(map(TableColumn, field_meta["columns"])),
            rows=list(map(TableRow, field_meta["rows"])),
            cells=cells,
            id_=EntityId(table_row["id"]),
        )
        if source_bbox_coordinates := build_source_bbox_coordinates_from_dict(table_row["source_bbox_coordinates"]):
            table.source_bbox_coordinates = source_bbox_coordinates
        source_table_coordinates = SourceTableCoordinatesMapper.from_dict(table_row["source_table_coordinates"])
        if source_table_coordinates is not None:
            table.source_table_coordinates = source_table_coordinates

        return table

    def sort_cell_list(
        self,
        raw_fields: list[Union[RowProxy, CommonDictType]],
    ) -> list[Union[RowProxy, CommonDictType]]:
        cell_number_index = self._get_cell_order_number_index(raw_fields)
        return sorted(raw_fields, key=lambda x: int(x["index"].split(".")[cell_number_index]))

    @staticmethod
    def build_table_cell_coordinates(coordinates: TableCellCoordinates) -> dict[str, int]:
        return {
            "column": coordinates.column,
            "row": coordinates.row,
            "column_span": coordinates.column_span,
            "row_span": coordinates.row_span,
        }

    def _get_cell_order_number_index(self, raw_fields: list[Union[RowProxy, CommonDictType]]) -> int:
        index_item_list = self._get_cell_index_item_list(raw_fields)
        cell_anchor_index = index_item_list.index("cell")
        return cell_anchor_index + 1

    @staticmethod
    def _get_cell_index_item_list(raw_fields: list[Union[RowProxy, CommonDictType]]) -> list[str]:
        return raw_fields[FIRST_ELEMENT]["index"].split(".")

    @staticmethod
    def _build_coordinates_from_table_coordinates(coordinates: TableCellCoordinates) -> dict[str, int]:
        return {
            "column": coordinates.column,
            "row": coordinates.row,
            "column_span": coordinates.column_span,
            "row_span": coordinates.row_span,
        }
