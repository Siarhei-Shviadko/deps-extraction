from deps_extraction.domain.types import RawCommandReply


def test_save_extraction_workflow__ok(extraction_workflow_repository, test_extraction_workflow_with_steps):
    test_extraction_workflow_with_steps.current_step.raw_command
    extraction_workflow_repository.save(test_extraction_workflow_with_steps)

    saved_workflow = extraction_workflow_repository.get(test_extraction_workflow_with_steps.id())

    assert saved_workflow == test_extraction_workflow_with_steps
    assert saved_workflow.document_id == test_extraction_workflow_with_steps.document_id
    assert saved_workflow.current_step == test_extraction_workflow_with_steps.current_step

    for saved_step, original_step in zip(saved_workflow.steps, test_extraction_workflow_with_steps.steps):
        assert saved_step == original_step
        assert saved_step.raw_command == original_step.raw_command


def test_save_extraction_workflow__several_times__ok(
    extraction_workflow_repository,
    test_extraction_workflow_with_steps,
):
    extraction_workflow_repository.save(test_extraction_workflow_with_steps)
    reply = RawCommandReply(
        workflow_id=test_extraction_workflow_with_steps.id(),
        step_id="",
        error=None,
        error_message=None,
    )
    for _ in range(len(test_extraction_workflow_with_steps.steps) - 1):
        reply["step_id"] = test_extraction_workflow_with_steps.current_step.id()
        test_extraction_workflow_with_steps.iter_workflow(reply)
        saved_workflow = extraction_workflow_repository.get(test_extraction_workflow_with_steps.id())

        assert saved_workflow == test_extraction_workflow_with_steps
