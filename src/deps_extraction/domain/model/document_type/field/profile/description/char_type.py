from enum import StrEnum

__all__ = ["CharType"]


class CharType(StrEnum):
    NUMERIC = "numeric"
    ALPHABETIC = "alphabetic"
    ALPHANUMERIC = "alphanumeric"
    BOOLEAN = "boolean"

    def __str__(self):
        return str(self.value)
