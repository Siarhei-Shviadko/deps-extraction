from typing import Optional

from pydantic import Field

from deps_extraction.domain.model import (
    FieldType,
    TableColumnDescription,
    TableFieldDescription,
)

from ....configured_base_serializer import ConfiguredBaseSerializer
from .type_mapping import GENERIC_DESCRIPTION_MAP, DescriptionGenericType

__all__ = ["SerializedTableDescription"]


class SerializedColumnDescription(ConfiguredBaseSerializer):
    title: str
    column_type: FieldType = Field(alias="columnType")
    column_data: Optional[DescriptionGenericType] = Field(None, alias="columnMeta")

    def to_model(self) -> TableColumnDescription:
        return TableColumnDescription(
            title=self.title,
            column_type=self.column_type,
            column_data=self.column_data.to_model() if self.column_data else None,
        )

    @classmethod
    def from_model(cls, description: TableColumnDescription) -> "SerializedColumnDescription":
        column_data_serializer = GENERIC_DESCRIPTION_MAP.get(description.column_data.__class__)
        serialized_column_data = (
            column_data_serializer.from_model(description.column_data) if column_data_serializer else None
        )

        return cls(
            title=description.title,
            column_type=description.column_type,
            column_data=serialized_column_data,
        )


class SerializedTableDescription(ConfiguredBaseSerializer):
    columns: list[SerializedColumnDescription]

    def to_model(self) -> TableFieldDescription:
        return TableFieldDescription(columns=[column.to_model() for column in self.columns])

    @classmethod
    def from_model(cls, description: TableFieldDescription) -> "SerializedTableDescription":
        return cls(
            columns=[SerializedColumnDescription.from_model(column) for column in description.columns],
        )
