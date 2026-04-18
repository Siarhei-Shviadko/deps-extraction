from deps_extracted_data.model import TableCellCoordinates, TableMeta, TableRow


def table_meta(table_meta: TableMeta):
    return {
        "chunksTotal": table_meta.chunks_total,
        "rowsTotal": table_meta.rows_total,
        "listIndex": table_meta.list_index,
    }


def table_paginated_rows(paginated_rows: list[list[TableRow]]):
    return [[{"y": row.y} for row in chunk] for chunk in paginated_rows]


def table_cell_coordinates_dict(table_coordinates: TableCellCoordinates) -> dict[str, int]:
    return {
        "column": table_coordinates.column,
        "row": table_coordinates.row,
        "column_span": table_coordinates.column_span,
        "row_span": table_coordinates.row_span,
    }
