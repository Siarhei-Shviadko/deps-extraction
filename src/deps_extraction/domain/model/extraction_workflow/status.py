from enum import StrEnum

__all__ = ["Status"]


class Status(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
