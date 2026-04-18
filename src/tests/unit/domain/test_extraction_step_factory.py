from uuid import uuid4

from deps_extraction.domain.events import (
    ExtractDocument,
    PerformCloudNativeExtraction,
    PerformLLMExtraction,
    PerformPrototypeExtraction,
    PerformTemplateExtraction,
)
from deps_extraction.domain.model import ExtractionStepFactory, ExtractorType
from deps_extraction.domain.model.extraction_workflow.extraction_step.destination import (
    Destination,
)


def test_extraction_step_factory__step_for_plugin__ok(perform_extraction_payload):
    step = ExtractionStepFactory(
        workflow_id=uuid4().hex, document_type_id=uuid4().hex, command_channel=uuid4().hex, **perform_extraction_payload
    ).make_for(uuid4().hex, ExtractorType.PLUGIN)
    assert isinstance(step.raw_command["command"], ExtractDocument)
    assert step.raw_command["headers"]["routing_info"]["commandreply_destination"] == "ExtractionService"
    assert step.raw_command["headers"]["routing_info"]["commandreply_reply_to"] == "DocumentProcessingSaga-reply"
    assert step.raw_command["reply_to"] == "ExtractionCommandsReplies"
    assert "workflow_id" in step.raw_command["headers"]["metadata"]
    assert "step_id" in step.raw_command["headers"]["metadata"]


def test_extraction_step_factory__step_for_template__ok(perform_extraction_payload):
    step = ExtractionStepFactory(
        workflow_id=uuid4().hex, document_type_id=uuid4().hex, command_channel=uuid4().hex, **perform_extraction_payload
    ).make_for(uuid4().hex, ExtractorType.TEMPLATE)

    assert step.raw_command["channel"] == Destination.TEMPLATE_SERVICE
    assert isinstance(step.raw_command["command"], PerformTemplateExtraction)
    assert step.raw_command["headers"]["command_destination"] == "ExtractionService"
    assert step.raw_command["headers"]["command_reply_to"] == "ExtractionCommandsReplies"
    assert step.raw_command["reply_to"] == "ExtractionCommandsReplies"
    assert "workflow_id" in step.raw_command["headers"]["metadata"]
    assert "step_id" in step.raw_command["headers"]["metadata"]


def test_extraction_step_factory__step_for_prototype__ok(perform_extraction_payload):
    step = ExtractionStepFactory(
        workflow_id=uuid4().hex, document_type_id=uuid4().hex, command_channel=uuid4().hex, **perform_extraction_payload
    ).make_for(uuid4().hex, ExtractorType.PROTOTYPE)

    assert step.raw_command["channel"] == Destination.PROTOTYPE_SERVICE
    assert isinstance(step.raw_command["command"], PerformPrototypeExtraction)
    assert step.raw_command["headers"]["command_destination"] == "ExtractionService"
    assert step.raw_command["headers"]["command_reply_to"] == "ExtractionCommandsReplies"
    assert step.raw_command["reply_to"] == "ExtractionCommandsReplies"
    assert "workflow_id" in step.raw_command["headers"]["metadata"]
    assert "step_id" in step.raw_command["headers"]["metadata"]


def test_extraction_step_factory__step_for_azure_cloud__ok(perform_extraction_payload):
    step = ExtractionStepFactory(
        workflow_id=uuid4().hex, document_type_id=uuid4().hex, command_channel=uuid4().hex, **perform_extraction_payload
    ).make_for(uuid4().hex, ExtractorType.AZURE_CLOUD_EXTRACTOR)

    assert step.raw_command["channel"] == Destination.CLOUD_NATIVE_EXTRACTION_SERVICE
    assert isinstance(step.raw_command["command"], PerformCloudNativeExtraction)
    assert step.raw_command["headers"]["command_destination"] == "ExtractionService"
    assert step.raw_command["headers"]["command_reply_to"] == "ExtractionCommandsReplies"
    assert step.raw_command["reply_to"] == "ExtractionCommandsReplies"
    assert "workflow_id" in step.raw_command["headers"]["metadata"]
    assert "step_id" in step.raw_command["headers"]["metadata"]


def test_extraction_step_factory__step_for_llm__ok(perform_extraction_payload):
    step = ExtractionStepFactory(
        workflow_id=uuid4().hex, document_type_id=uuid4().hex, command_channel=uuid4().hex, **perform_extraction_payload
    ).make_for(uuid4().hex, ExtractorType.LLM)

    assert step.raw_command["channel"] == Destination.AI_FUSION_SERVICE
    assert isinstance(step.raw_command["command"], PerformLLMExtraction)
    assert step.raw_command["headers"]["command_destination"] == "ExtractionService"
    assert step.raw_command["headers"]["command_reply_to"] == "ExtractionCommandsReplies"
    assert step.raw_command["reply_to"] == "ExtractionCommandsReplies"
    assert "workflow_id" in step.raw_command["headers"]["metadata"]
    assert "step_id" in step.raw_command["headers"]["metadata"]
