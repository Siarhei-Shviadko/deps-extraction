from typing import Any, Optional

from .....shared import Guard, ImmutableCheck
from ..field_type import FieldType
from .description import FieldDescription

__all__ = ["TableFieldDescription", "TableColumnDescription"]


class TableColumnDescription:
    title = Guard[str](str, ImmutableCheck())
    column_type = Guard[FieldType](FieldType, ImmutableCheck())
    column_data = Guard[FieldDescription](FieldDescription, ImmutableCheck())

    def __init__(
        self,
        title: str,
        column_type: FieldType,
        column_data: Optional[FieldDescription],
        **kwargs: Optional[int],
    ) -> None:
        super().__init__(**kwargs)  # type: ignore
        self.title = title
        self.column_type = column_type
        if column_data is not None:
            self.column_data = column_data

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.title == other.title
            and self.column_type == other.column_type
            and self.column_data == other.column_data
        )

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__name__}': "
            f"{self.title = }, "
            f"{self.column_type = }, "
            f"{self.column_data = }>"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "column_type": self.column_type,
            "column_data": self.column_data.to_dict() if self.column_data else None,
        }


class TableFieldDescription(FieldDescription):
    columns = Guard[list[TableColumnDescription]](list, ImmutableCheck())

    def __init__(self, columns: list[TableColumnDescription]) -> None:
        self.columns = columns

    def belongs_to_type(self, type_: FieldType) -> bool:
        return type_ == FieldType.TABLE

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and len(self.columns) == len(other.columns)
            and all(
                column1 == column2
                for column1, column2 in zip(
                    sorted(self.columns, key=lambda _column: _column.title),
                    sorted(other.columns, key=lambda _column: _column.title),
                )
            )
        )

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}': " f"{self.columns = }>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "columns": [column.to_dict() for column in self.columns],
        }
