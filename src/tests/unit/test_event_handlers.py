import json

from deps_message_flow.commands.common import CommandReplyOutcome

from deps_extraction.domain.events import PerformExtractionReply
from deps_extraction.domain.model import ExtractorType
from deps_extraction.domain.model.extraction_workflow.extraction_step.destination import (
    Destination,
)
from deps_extraction.messaging.handlers import (
    get_document_types_reply_handler,
    perform_extraction_handler,
)


def test_perform_extraction__plugin__success(
    perform_extraction_command_message,
    fake_document_type_repository,
    fake_message_producer,
    test_document_type_with_plugin_extractor,
):
    command = perform_extraction_command_message.command
    expected_payload = {
        "document_id": command.document_id,
        "language": command.language,
        "engine": command.engine,
    }
    fake_document_type_repository.save(test_document_type_with_plugin_extractor)

    perform_extraction_handler(perform_extraction_command_message)

    message_info = fake_message_producer[0]
    sent_headers = message_info[1].headers
    assert message_info[0] == test_document_type_with_plugin_extractor.command_channel
    assert json.loads(message_info[1].payload) == expected_payload
    assert sent_headers["routing_info"] == perform_extraction_command_message.correlation_headers


def test_perform_extraction__template__success(
    perform_extraction_command_message,
    fake_document_type_repository,
    fake_message_producer,
    test_document_type_with_template_extractors,
):
    command = perform_extraction_command_message.command
    expected_payload = {
        "document_id": int(command.document_id),
        "template_id": command.document_type_id,
        "tenant_id": command.tenant_id,
        "language": command.language,
        "engine": command.engine,
        "version_id": command.extra_data["template_version_id"],
    }

    fake_document_type_repository.save(test_document_type_with_template_extractors)

    perform_extraction_handler(perform_extraction_command_message)

    message_info = fake_message_producer[0]
    sent_headers = message_info[1].headers

    assert message_info[0] == Destination.TEMPLATE_SERVICE
    assert json.loads(message_info[1].payload) == expected_payload
    assert sent_headers["command_saga_id"] == perform_extraction_command_message.message.headers["command_saga_id"]


def test_perform_extraction__prototype__success(
    perform_extraction_command_message,
    fake_document_type_repository,
    fake_message_producer,
    test_document_type_with_prototype_extractors,
):
    command = perform_extraction_command_message.command
    expected_payload = {
        "document_id": int(command.document_id),
        "prototype_id": command.document_type_id,
        "tenant_id": command.tenant_id,
        "language": command.language,
        "engine": command.engine,
    }

    fake_document_type_repository.save(test_document_type_with_prototype_extractors)

    perform_extraction_handler(perform_extraction_command_message)

    message_info = fake_message_producer[0]
    sent_headers = message_info[1].headers
    assert message_info[0] == Destination.PROTOTYPE_SERVICE
    assert json.loads(message_info[1].payload) == expected_payload
    assert sent_headers["command_saga_id"] == perform_extraction_command_message.message.headers["command_saga_id"]


def test_perform_extraction__non_type__success(
    perform_extraction_command_message,
    fake_document_type_repository,
    fake_message_producer,
    test_document_type_llm_extractor_with_field,
):
    command = perform_extraction_command_message.command
    expected_payload = {
        "document_id": command.document_id,
        "extractor_id": next(
            (
                extractor
                for extractor in test_document_type_llm_extractor_with_field.extractors.values()
                if extractor.type == ExtractorType.LLM
            )
        ).id(),
        "llm_type": None,
    }

    fake_document_type_repository.save(test_document_type_llm_extractor_with_field)

    perform_extraction_handler(perform_extraction_command_message)

    message_info = fake_message_producer[0]
    sent_headers = message_info[1].headers
    assert message_info[0] == Destination.AI_FUSION_SERVICE
    assert json.loads(message_info[1].payload) == expected_payload

    assert sent_headers["command_saga_id"] == perform_extraction_command_message.message.headers["command_saga_id"]


def test_get_document_types_reply_handler__success(
    get_document_types_reply_message,
    fake_document_type_repository,
    raw_document_types,
):
    get_document_types_reply_message.message.get_required_header.return_value = CommandReplyOutcome.SUCCESS.name

    get_document_types_reply_handler(get_document_types_reply_message)

    for document_type in raw_document_types:
        assert fake_document_type_repository.get(document_type["document_type_id"])


def test_get_document_types_reply_handler__failure__no_error(
    get_document_types_reply_message,
    fake_document_type_repository,
    raw_document_types,
):
    get_document_types_reply_message.message.get_required_header.return_value = CommandReplyOutcome.FAILURE.name

    get_document_types_reply_handler(get_document_types_reply_message)

    for document_type in raw_document_types:
        assert not fake_document_type_repository.get(document_type["document_type_id"])
