import logging
from typing import Optional

from ...exceptions import (
    ExtractionWorkflowExecutionError,
    ExtractionWorkflowExhaustedError,
)
from ...types import RawCommand, RawCommandReply
from ..shared import EntityId, Guard, ImmutableCheck
from .extraction_step import ErrorType, ExtractionStep, StepStatus
from .status import Status

__all__ = ["ExtractionWorkflow"]

FIRST_ELEMENT = 0
LAST_ELEMENT = -1


class ExtractionWorkflow:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    document_id = Guard[str](str, ImmutableCheck())
    steps = Guard[list[ExtractionStep]](list)
    current_step_index = Guard[int](int)

    def __init__(
        self,
        id_: EntityId,
        document_id: str,
        steps: list[ExtractionStep],
        *,
        current_step_index: Optional[int] = None,
    ) -> None:
        self.id = id_
        self.document_id = document_id
        self.current_step_index = current_step_index if current_step_index is not None else FIRST_ELEMENT

        self.steps = steps

        self._logger = logging.getLogger(self.__class__.__name__)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id_={repr(self.id)}, "
            f"document_id={repr(self.document_id)}, "
            f"steps={repr(self.steps)}"
            f"current_step_index={repr(self.current_step_index)})"
        )

    def __str__(self) -> str:
        steps_summary = f"{len(self.steps)} steps"
        return (
            f"ExtractionWorkflow: id={self.id}, "
            f"document_id={self.document_id}, "
            f"steps={steps_summary}, "
            f"current_step_index={self.current_step_index}"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    @property
    def current_step(self) -> Optional[ExtractionStep]:
        if self.status != Status.PENDING:
            return None

        try:
            return self._extraction_steps[self.current_step_index]
        except IndexError:
            return None

    @property
    def failed_steps(self) -> list[ExtractionStep]:
        return [step for step in self._extraction_steps if step.status == StepStatus.FAILED]

    @property
    def _extraction_steps(self) -> list[ExtractionStep]:
        return self.steps[:LAST_ELEMENT]

    @property
    def _extraction_reply(self) -> ExtractionStep:
        if self.status == Status.PENDING:
            ExtractionWorkflowExecutionError("ExtractionReply can't be called in Pending status of ExtractionWorkflow.")

        if (step := self.steps[LAST_ELEMENT]).status == StepStatus.PENDING:
            first_failed_step = self.failed_steps[FIRST_ELEMENT] if self.failed_steps else None

            step.complete_step_with(
                error_type=first_failed_step.error.error_type if first_failed_step else None,
                error_message=first_failed_step.error.error_message if first_failed_step else None,
            )
            return step

        raise ExtractionWorkflowExhaustedError("ExtractionReply can be gotten only ones.")

    @property
    def status(self) -> Status:
        step_statuses = {step.status for step in self._extraction_steps}

        if StepStatus.FAILED in step_statuses:
            return Status.FAILED

        elif StepStatus.PENDING in step_statuses:
            return Status.PENDING

        return Status.COMPLETED

    def start_workflow(self) -> RawCommand:
        if self.current_step_index == FIRST_ELEMENT:
            return self.current_step.raw_command

        raise ExtractionWorkflowExecutionError("ExtractionWorkflow can be started only once.")

    def iter_workflow(self, reply: RawCommandReply) -> RawCommand:
        self._complete_step_from(reply)
        next_command = self._find_next_step()
        return next_command.raw_command

    def _find_next_step(self) -> ExtractionStep:
        if self.status == Status.FAILED:
            return self._extraction_reply

        return self.current_step or self._extraction_reply

    def _complete_step_from(self, reply: RawCommandReply) -> None:
        step = next(filter(lambda step: step.id() == reply["step_id"], self.steps))

        step.complete_step_with(
            error_type=ErrorType(reply["error"]) if reply["error"] else None,
            error_message=reply["error_message"],
        )
        self.current_step_index += 1
