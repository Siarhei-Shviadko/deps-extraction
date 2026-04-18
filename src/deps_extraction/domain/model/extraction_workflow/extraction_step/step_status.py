from enum import StrEnum

__all__ = ["StepStatus"]


class StepStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
