import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_extraction.constants import (
    CLOUD_NATIVE_EXTRACTION_EXCHANGER,
    COMMANDS_QUEUE,
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_TYPE_EXCHANGER,
    DOCUMENTS_EXCHANGER,
    EXTRACTION_FIELDS_DESTINATION,
    QUEUE,
    SERVICE_CHANNEL,
    TEMPLATE_EXCHANGER,
)
from deps_extraction.domain.events import (
    CloudExtractorFieldCreated,
    CloudExtractorFieldDeleted,
    CloudExtractorFieldUpdated,
    DocumentDeleted,
    DocumentTypeChanged,
    DocumentTypeCreated,
    DocumentTypeDeleted,
    ExtractionFieldsMoved,
    ExtractorFieldsDuplicated,
    GetDocumentTypesReply,
    PerformExtraction,
    PerformExtractionStepReply,
)

_logger = logging.getLogger(__name__)


def make_message_dispatcher(subscriber: IMessageConsumer, producer: IMessageProducer) -> IMessageConsumer:
    from deps_extraction.messaging.handlers import (  # noqa: WPS433
        cloud_extractor_field_created,
        cloud_extractor_field_deleted,
        cloud_extractor_field_updated,
        document_deleted_handler,
        document_type_changed_handler,
        document_type_created_handler,
        document_type_deleted_handler,
        extraction_fields_moved_handler,
        extractor_fields_duplicate_handler,
        get_document_types_reply_handler,
        perform_extraction_handler,
        perform_extraction_step_reply_handler,
    )

    events_handlers = (
        DomainEventHandlersBuilder.for_aggregate_type(DOCUMENT_TYPE_EXCHANGER)
        .on_event(DocumentTypeCreated, document_type_created_handler)
        .on_event(DocumentTypeDeleted, document_type_deleted_handler)
        .and_for_aggregate_type(DOCUMENTS_EXCHANGER)
        .on_event(DocumentDeleted, document_deleted_handler)
        .on_event(DocumentTypeChanged, document_type_changed_handler)
        .and_for_aggregate_type(TEMPLATE_EXCHANGER)
        .on_event(ExtractorFieldsDuplicated, extractor_fields_duplicate_handler)
        .and_for_aggregate_type(CLOUD_NATIVE_EXTRACTION_EXCHANGER)
        .on_event(CloudExtractorFieldCreated, cloud_extractor_field_created)
        .on_event(CloudExtractorFieldUpdated, cloud_extractor_field_updated)
        .on_event(CloudExtractorFieldDeleted, cloud_extractor_field_deleted)
        .and_for_aggregate_type(EXTRACTION_FIELDS_DESTINATION)
        .on_event(ExtractionFieldsMoved, extraction_fields_moved_handler)
        .for_queue(QUEUE)
        .build()
    )

    commands_handlers = (
        CommandHandlersBuilder.from_channel(COMMANDS_REPLIES_CHANNEL)
        .on_message(GetDocumentTypesReply, get_document_types_reply_handler)
        .on_message(PerformExtractionStepReply, perform_extraction_step_reply_handler)
        .and_from_channel(SERVICE_CHANNEL)
        .on_message(PerformExtraction, perform_extraction_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    ded = DomainEventDispatcher(events_handlers, subscriber)
    ded.initialize()

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    _logger.info("Start consuming....")

    return subscriber
