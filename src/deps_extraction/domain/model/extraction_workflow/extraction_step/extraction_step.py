import logging
from typing import Optional

from ....exceptions import ExtractionStepException
from ....types import RawCommand
from ...shared import EntityId, Guard, ImmutableCheck
from .error import ErrorType, ExtractionStepError
from .step_status import StepStatus

__all__ = ["ExtractionStep"]


class ExtractionStep:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    status = Guard[StepStatus](StepStatus)
    error = Guard[ExtractionStepError](ExtractionStepError, ImmutableCheck())

    def __init__(
        self,
        id_: EntityId,
        raw_command: RawCommand,
        status: StepStatus = StepStatus.PENDING,
        error: Optional[ExtractionStepError] = None,
    ) -> None:
        self.id = id_
        self.status = status
        self.raw_command = raw_command

        if error:
            self.error = error

        self._logger = logging.getLogger(self.__class__.__name__)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={repr(self.id)}, "
            f"raw_command={repr(self.raw_command)}, "
            f"status={repr(self.status)}, "
            f"error={repr(self.error)}"
        )

    def __str__(self) -> str:
        return (
            f"ExtractionStep: id={self.id}, "
            f"raw_command={self.raw_command}, "
            f"status={self.status}), "
            f"error={self.error}"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def complete_step_with(self, error_type: Optional[ErrorType] = None, error_message: Optional[str] = None) -> None:
        if self.status != StepStatus.PENDING:
            raise ExtractionStepException("ExtractionStep can be completed only once")

        if error_type:
            self.error = ExtractionStepError(error_type=error_type, error_message=error_message or "")
            self.status = StepStatus.FAILED
            self._add_error_to_command()

        else:
            self.status = StepStatus.COMPLETED

        self._logger.debug("Step %s completed with status: %s", self.id(), self.status)

    def _add_error_to_command(self) -> None:
        self.raw_command["command"].error_type = self.error.error_type
        self.raw_command["command"].error_message = self.error.error_message
