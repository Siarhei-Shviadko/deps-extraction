from typing import Any, Optional

from deps_extracted_data import CellCoordinates, CellRange, SourceTableCoordinates

from deps_extraction.domain.dtos import ExtractedDataPaginationParamsObject

from ..types import CommonDictType, ListOfDictsType

__all__ = [
    "SourceTableCoordinatesMapper",
    "CellRangeMapper",
    "CellCoordinatesMapper",
]


class CellRangeMapper:
    @staticmethod
    def to_dict(cell_range: CellRange) -> CommonDictType:
        cell_range_dict = {"begin": CellCoordinatesMapper.to_dict(cell_range.begin)}
        if cell_range.end:
            cell_range_dict["end"] = CellCoordinatesMapper.to_dict(cell_range.end)
        return cell_range_dict

    @staticmethod
    def from_dict(cell_range_dict: CommonDictType) -> CellRange:
        cell_range = CellRange(begin=CellCoordinatesMapper.from_dict(cell_range_dict["begin"]))
        if end := cell_range_dict.get("end"):
            cell_range.end = CellCoordinatesMapper.from_dict(end)
        return cell_range


class CellCoordinatesMapper:
    @staticmethod
    def to_dict(cell_coordinates: CellCoordinates) -> CommonDictType:
        return {
            "row": cell_coordinates.row,
            "column": cell_coordinates.column,
        }

    @staticmethod
    def from_dict(cell_coordinates_dict: CommonDictType) -> CellCoordinates:
        return CellCoordinates(row=cell_coordinates_dict["row"], column=cell_coordinates_dict["column"])


class SourceTableCoordinatesMapper:
    @staticmethod
    def to_dict(table_coordinates: Optional[list[SourceTableCoordinates]]) -> Optional[ListOfDictsType]:
        if table_coordinates is None:
            return None
        return [
            {
                "source_id": coordinates.source_id.value,
                "cell_ranges": [CellRangeMapper.to_dict(cell_range) for cell_range in coordinates.cell_ranges],
            }
            for coordinates in table_coordinates
        ]

    @staticmethod
    def from_dict(table_dicts: Optional[ListOfDictsType]) -> Optional[list[SourceTableCoordinates]]:
        if table_dicts is None:
            return None
        return [
            SourceTableCoordinates(
                value=coordinates_dict["source_id"],
                cell_ranges=[CellRangeMapper.from_dict(cell_range) for cell_range in coordinates_dict["cell_ranges"]],
            )
            for coordinates_dict in table_dicts
        ]

    @staticmethod
    def build_chunk_table_coordinates(
        table_dicts: Optional[ListOfDictsType],
        pagination_params: ExtractedDataPaginationParamsObject,
    ) -> Optional[list[SourceTableCoordinates]]:
        if table_dicts is None:
            return None
        coordinates = table_dicts[0]["cell_ranges"][0]
        cell_ranges = [
            CellRangeMapper.from_dict(
                {
                    "begin": {
                        "column": coordinates["begin"]["column"],
                        "row": coordinates["begin"]["row"]
                        if pagination_params.original_data
                        else coordinates["begin"]["row"] - pagination_params.left_row_index,
                    },
                    "end": {
                        "column": coordinates["end"]["column"],
                        "row": coordinates["end"]["row"]  # noqa: WPS509
                        if pagination_params.original_data
                        else SourceTableCoordinatesMapper.choose_end_row(coordinates, pagination_params),
                    }
                    if coordinates.get("end")
                    else None,
                },
            ),
        ]
        return [SourceTableCoordinates(value=table_dicts[0]["source_id"], cell_ranges=cell_ranges)]

    @staticmethod
    def choose_end_row(cell_range: dict[str, Any], pagination_params: ExtractedDataPaginationParamsObject) -> int:
        if cell_range["end"]["row"] - cell_range["begin"]["row"] + 1 > pagination_params.rows_per_chunk:
            return min(cell_range["end"]["row"], pagination_params.rows_per_chunk - 1)
        return cell_range["end"]["row"] - pagination_params.left_row_index
