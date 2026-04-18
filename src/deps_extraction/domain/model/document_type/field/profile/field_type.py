from enum import StrEnum

__all__ = ["FieldType"]


class FieldType(StrEnum):
    STRING = "string"
    ENUM = "enum"
    DATE = "date"
    LIST = "list"
    DICT = "dict"
    TABLE = "table"
    CHECKMARK = "checkmark"

    def __str__(self):
        return str(self.value)
