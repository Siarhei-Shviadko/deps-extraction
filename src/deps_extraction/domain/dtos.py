from dataclasses import dataclass
from typing import Optional

__all__ = [
    "ExtractedDataListFilterObject",
    "TableFieldRowsRange",
    "ExtractedDataFilterObject",
    "ExtractedDataPaginationParamsObject",
]


@dataclass
class ExtractedDataListFilterObject:
    limit: Optional[int] = None
    offset: Optional[int] = None

    document_ids: Optional[list[int]] = None


@dataclass
class TableFieldRowsRange:
    left: int
    right: int


@dataclass
class ExtractedDataFilterObject:
    document_id: int
    field_codes: Optional[list[str]] = None
    field_types: Optional[list[str]] = None
    field_rows_range: Optional[TableFieldRowsRange] = None
    paginated_field_codes: Optional[list[str]] = None
    indexes: Optional[list[str]] = None


@dataclass
class ExtractedDataPaginationParamsObject:
    rows_per_chunk: int
    rows_chunk: int
    list_index: Optional[int] = None
    original_data: bool = False

    @property
    def left_row_index(self):
        return self.rows_per_chunk * (self.rows_chunk - 1)

    @property
    def right_row_index(self):
        return self.left_row_index + self.rows_per_chunk
