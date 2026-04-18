import logging
from typing import Optional

from deps_extraction.domain.model import (
    DateFieldDescription,
    FieldDescription,
    FieldType,
    TableColumnDescription,
    TableFieldDescription,
)
from deps_extraction.domain.types import RawDescription, RawTableDescription

__all__ = ["make_field_description", "make_table_field_description"]

_logger = logging.getLogger(__name__)


def make_table_field_description(raw_description: RawTableDescription) -> TableFieldDescription:
    return TableFieldDescription(
        columns=[
            TableColumnDescription(title=col["title"], column_type=FieldType(col["type"]), column_data=None)
            for col in raw_description["columns"]
        ],
    )


def make_field_description(raw_description: Optional[RawDescription]) -> FieldDescription:
    if raw_description is None:
        return FieldDescription()

    if format_ := raw_description.get("format"):
        return DateFieldDescription(format=format_)

    elif "columns" in raw_description:
        return make_table_field_description(raw_description)  # type: ignore

    _logger.warning("Can't define FieldDescription from: %s.\n Default FieldDescription set up.", raw_description)
    return FieldDescription()
