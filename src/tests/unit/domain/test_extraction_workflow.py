from copy import deepcopy

import pytest

from deps_extraction.domain.events import PerformExtractionReply
from deps_extraction.domain.exceptions import (
    ExtractionStepException,
    ExtractionWorkflowExecutionError,
    ExtractionWorkflowExhaustedError,
)
from deps_extraction.domain.model import ExtractionWorkflow, Status, StepStatus
from deps_extraction.domain.types import RawCommandReply


def _create_successful_command_reply(workflow: ExtractionWorkflow) -> RawCommandReply:
    return RawCommandReply(
        workflow_id=workflow.id(),
        step_id=workflow.current_step.id(),
        error=None,
        error_message=None,
    )


def _create_failed_command_reply(workflow: ExtractionWorkflow) -> RawCommandReply:
    return RawCommandReply(
        workflow_id=workflow.id(),
        step_id=workflow.current_step.id(),
        error="business",
        error_message="Test error message",
    )


def test_workflow__initial_command__ok(test_extraction_workflow_with_steps):
    initial_command = test_extraction_workflow_with_steps.current_step.raw_command
    assert initial_command


def test_workflow__iter_workflow__ok(test_extraction_workflow_with_steps):
    test_extraction_workflow_with_steps.current_step.raw_command

    for _ in range(len(test_extraction_workflow_with_steps.steps) - 2):
        reply = _create_successful_command_reply(test_extraction_workflow_with_steps)
        test_extraction_workflow_with_steps.iter_workflow(reply)

    extraction_reply = test_extraction_workflow_with_steps.iter_workflow(
        _create_successful_command_reply(test_extraction_workflow_with_steps)
    )

    command = extraction_reply["command"]
    assert test_extraction_workflow_with_steps.status == Status.COMPLETED
    assert isinstance(command, PerformExtractionReply)
    assert (command.error_message, command.error_type) == (None, None)
    assert not test_extraction_workflow_with_steps.failed_steps


def test_workflow__iter_workflow__failed_step__reply_generated(test_extraction_workflow_with_steps):
    first_reply = _create_failed_command_reply(test_extraction_workflow_with_steps)

    extraction_reply = test_extraction_workflow_with_steps.iter_workflow(first_reply)

    assert test_extraction_workflow_with_steps.status == Status.FAILED
    assert test_extraction_workflow_with_steps.current_step is None
    assert isinstance(extraction_reply["command"], PerformExtractionReply)
    assert extraction_reply["command"].error_message == first_reply["error_message"]
    assert extraction_reply["command"].error_type == first_reply["error"]
    assert len(test_extraction_workflow_with_steps.failed_steps) == 1
    assert test_extraction_workflow_with_steps.failed_steps[0].error.error_type == first_reply["error"]
    assert test_extraction_workflow_with_steps.failed_steps[0].error.error_message == first_reply["error_message"]

    for step in test_extraction_workflow_with_steps.steps[1:-1]:
        assert step.status == StepStatus.PENDING
        assert step.error is None


def test_workflow__iter_workflow__extraction_workflow_failed__error(test_extraction_workflow_with_steps):
    first_reply = _create_failed_command_reply(test_extraction_workflow_with_steps)
    second_reply = deepcopy(first_reply)
    second_reply["step_id"] = test_extraction_workflow_with_steps.steps[1].id()

    test_extraction_workflow_with_steps.iter_workflow(first_reply)

    with pytest.raises(ExtractionWorkflowExhaustedError):
        assert test_extraction_workflow_with_steps.current_step is None
        assert test_extraction_workflow_with_steps.status == Status.FAILED
        test_extraction_workflow_with_steps.iter_workflow(second_reply)


def test_workflow__iter_workflow__complete_step_twice__error(test_extraction_workflow_with_steps):
    reply = _create_successful_command_reply(test_extraction_workflow_with_steps)
    test_extraction_workflow_with_steps.iter_workflow(reply)

    with pytest.raises(ExtractionStepException):
        test_extraction_workflow_with_steps.iter_workflow(reply)


def test_workflow__start_worfklow__ok(test_extraction_workflow_with_steps):
    initial_command = test_extraction_workflow_with_steps.start_workflow()

    assert initial_command
    assert initial_command == test_extraction_workflow_with_steps.steps[0].raw_command


def test_workflow__start_worfklow_twice__error(test_extraction_workflow_with_steps):
    test_extraction_workflow_with_steps.start_workflow()
    test_extraction_workflow_with_steps.iter_workflow(
        _create_successful_command_reply(test_extraction_workflow_with_steps)
    )

    with pytest.raises(ExtractionWorkflowExecutionError):
        test_extraction_workflow_with_steps.start_workflow()
