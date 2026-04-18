from typing import Any

from deps_extracted_data.model import (
    Bbox,
    SourceBboxCoordinates,
    SourceTableCoordinates,
    SourceTextCoordinates,
)


def bbox_dict(bbox: Bbox) -> dict[str, float]:
    return {
        "x": bbox.x,
        "y": bbox.y,
        "w": bbox.w,
        "h": bbox.h,
    }


def source_bbox_coordinates_dict(source_bbox_coordinates: SourceBboxCoordinates) -> dict[str, Any]:
    return {
        "sourceId": source_bbox_coordinates.source_id.value,
        "bboxes": [bbox_dict(i) for i in source_bbox_coordinates.bboxes],
    }


def source_table_coordinates_dict(source_table_coordinates: SourceTableCoordinates) -> dict[str, Any]:
    return {
        "sourceId": source_table_coordinates.source_id.value,
        "cellRanges": [
            {
                "begin": {"row": cell_range.begin.row, "column": cell_range.begin.column},
                "end": {"row": cell_range.end.row, "column": cell_range.end.column} if cell_range.end else None,
            }
            for cell_range in source_table_coordinates.cell_ranges
        ],
    }


def source_text_coordinates_dict(source_text_coordinates: SourceTextCoordinates) -> dict[str, Any]:
    return {
        "sourceId": source_text_coordinates.source_id.value,
        "charRanges": [
            {"begin": char_range.begin, "end": char_range.end} for char_range in source_text_coordinates.char_ranges
        ],
    }
