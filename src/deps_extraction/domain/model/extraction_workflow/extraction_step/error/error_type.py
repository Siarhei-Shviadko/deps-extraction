from enum import StrEnum

__all__ = ["ErrorType"]


class ErrorType(StrEnum):
    SYSTEM = "system"
    BUSINESS = "business"
