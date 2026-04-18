from typing import Any, Mapping

from deps_extraction.domain.model import (
    FieldType,
    TableColumnDescription,
    TableFieldDescription,
)

from .base_types_mapping import BASE_TYPES_MAPPING

__all__ = ["TableDescriptionMapper"]


class TableColumnDescriptionMapper:
    @staticmethod
    def from_dict(raw_column_description: Mapping[str, Any]) -> TableColumnDescription:
        column_type = FieldType(raw_column_description["column_type"])
        column_type_class = BASE_TYPES_MAPPING[column_type]

        return TableColumnDescription(
            title=raw_column_description["title"],
            column_type=column_type,
            column_data=column_type_class.from_dict(raw_column_description["column_data"])
            if raw_column_description.get("column_data")
            else None,
        )

    @staticmethod
    def to_dict(description: TableColumnDescription) -> Mapping[str, Any]:
        item_type_class = BASE_TYPES_MAPPING[description.column_type]
        return {
            "title": description.title,
            "column_type": description.column_type.value,
            "column_data": item_type_class.to_dict(description.column_data) if description.column_data else None,
        }


class TableDescriptionMapper:
    @staticmethod
    def from_dict(raw_description: Mapping[str, Any]) -> TableFieldDescription:
        columns_description = [
            TableColumnDescriptionMapper.from_dict(column_description)
            for column_description in raw_description["columns"]
        ]
        return TableFieldDescription(columns=columns_description)

    @staticmethod
    def to_dict(description: TableFieldDescription) -> Mapping[str, Any]:
        columns_description = [
            TableColumnDescriptionMapper.to_dict(column_description) for column_description in description.columns
        ]
        return {"columns": columns_description}
