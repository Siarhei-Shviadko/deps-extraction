import contextlib
import json
import logging
from typing import Optional

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import (
    CommandMessageHeaders,
    CommandReplyOutcome,
    ReplyMessageHeaders,
    make_message_for_command,
)
from deps_message_flow.commands.consumer import CommandHandlerReplyBuilder
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from deps_message_flow.messaging.common.interfaces import IMessage

from deps_extraction.api.auth import get_current_user_tenant
from deps_extraction.api.serializers import SerializedDocumentType
from deps_extraction.application import DocumentTypeService, ExtractedDataService
from deps_extraction.containers import Containers
from deps_extraction.domain.events import (
    CloudExtractorFieldCreated,
    CloudExtractorFieldDeleted,
    CloudExtractorFieldUpdated,
    DocumentTypeCreated,
    ExtractionFieldsMoved,
    ExtractorFieldsDuplicated,
    GetDocumentTypesReply,
    PerformExtraction,
    PerformExtractionReply,
    PerformExtractionStepReply,
)
from deps_extraction.domain.exceptions import BusinessException, NotFoundError
from deps_extraction.domain.model import ErrorType, FieldType, RawDocumentType
from deps_extraction.domain.types import RawCommandReply

from .utils import make_field_description, make_table_field_description

logger = logging.getLogger(__name__)

REPLY_TO_MOCK = "NONE"


def is_command_successful(command_message: CommandMessage) -> bool:
    return (
        command_message.message.get_required_header(ReplyMessageHeaders.REPLY_OUTCOME)
        == CommandReplyOutcome.SUCCESS.name
    )


@inject
def document_type_created_handler(
    dee: DomainEventEnvelope[DocumentTypeCreated],
    application: DocumentTypeService = Provide[Containers.application.document_type],
) -> None:
    application.save_new_document_type(
        document_type_id=dee.event.document_type,
        tenant_id=dee.event.tenant,
        name=dee.event.name,
    )


@inject
def get_document_types_reply_handler(  # noqa: WPS463
    command_message: CommandMessage[GetDocumentTypesReply],
    application: DocumentTypeService = Provide[Containers.application.document_type],
) -> None:
    if is_command_successful(command_message):
        serialized_document_types = [
            SerializedDocumentType(
                id=document_type["document_type_id"],
                tenant_id=document_type["tenant_id"],
                document_type=document_type["name"],
                extraction_type=document_type["extraction_type"],
                fields=[],
            )
            for document_type in command_message.command.document_types
        ]

        raw_document_types: list[RawDocumentType] = []  # type: ignore

        for serialized_dt in serialized_document_types:
            raw_document_types.append(
                {
                    "document_type_id": serialized_dt.id,
                    "tenant_id": serialized_dt.tenant_id,
                    "name": serialized_dt.document_type,
                    "extraction_type": serialized_dt.extraction_type,
                },
            )

        application.save_new_document_types(raw_document_types)

        logger.info("Document types updated successfully")

    else:
        logger.error(f"Failed to get document types. Command headers: {command_message.message.headers}")


def document_deleted_handler(dee: DomainEventEnvelope) -> None:
    _delete_extracted_data(document_id=int(dee.event.document_id))


def document_type_changed_handler(dee: DomainEventEnvelope) -> None:
    _delete_extracted_data(document_id=int(dee.event.document_id))


@inject
def perform_extraction_handler(
    command_message: CommandMessage,
    application: DocumentTypeService = Provide[Containers.application.document_type],
) -> Optional[list[IMessage]]:
    command: PerformExtraction = command_message.command
    error_type = None
    error_message = None

    try:
        application.extract_document(
            document_id=command.document_id,
            document_type_id=command.document_type_id,
            tenant_id=command.tenant_id,
            template_version_id=command.extra_data.get("template_version_id"),
            language=command.language,
            engine=command.engine,
            llm_type=command.llm_type,
            correlation_headers=command_message.correlation_headers,
            extra_headers=command_message.message.headers,
        )
    except BusinessException as e:
        error_type, error_message = ErrorType.BUSINESS, str(e)
    except Exception as e:
        error_type, error_message = ErrorType.SYSTEM, str(e)

    if error_type is not None:
        logger.error(
            f"Failed to extract document with id {command_message.command.document_id}! \n Reason: {error_message}",
        )

        reply = PerformExtractionReply(error_type, error_message)
        reply_command_message = make_message_for_command(
            channel=REPLY_TO_MOCK,
            payload=JsonMapper().serialize(reply),
            command_type=reply.__class__.__name__,
            reply_to=REPLY_TO_MOCK,
        )
        return [CommandHandlerReplyBuilder.with_success(reply_command_message)]


@inject
def document_type_deleted_handler(
    dee: DomainEventEnvelope,
    application: DocumentTypeService = Provide[Containers.application.document_type],
) -> None:
    with contextlib.suppress(NotFoundError):
        application.delete_document_type(
            document_type_id=dee.event.document_type,
            tenant_id=dee.event.tenant,
        )


@inject
def _delete_extracted_data(
    document_id: int,
    application: ExtractedDataService = Provide[Containers.application.extracted_data],
) -> None:
    application.delete_extracted_data(document_id=document_id)


@inject
def extractor_fields_duplicate_handler(
    dee: DomainEventEnvelope[ExtractorFieldsDuplicated],
    application: DocumentTypeService = Provide[Containers.application.document_type],
) -> None:
    application.copy_fields(
        tenant_id=get_current_user_tenant(),
        source_document_type_id=dee.event.source_document_type_code,
        target_document_type_id=dee.event.target_document_type_code,
    )


@inject
def cloud_extractor_field_created(
    dee: DomainEventEnvelope[CloudExtractorFieldCreated],
    application: DocumentTypeService = Provide[Containers.application.document_type],
    current_user_tenant: str = Provide[Containers.current_user_tenant],
) -> None:
    application.create_field(
        document_type_id=dee.event.document_type_id,
        tenant_id=current_user_tenant,
        code=dee.event.code,
        name=dee.event.name,
        type_=FieldType(dee.event.type),
        description=make_field_description(dee.event.description),
        required=dee.event.required,
        order=dee.event.order,
    )


@inject
def cloud_extractor_field_updated(
    dee: DomainEventEnvelope[CloudExtractorFieldUpdated],
    application: DocumentTypeService = Provide[Containers.application.document_type],
    current_user_tenant: str = Provide[Containers.current_user_tenant],
) -> None:
    # We can update only table description for Fields generated by CloudExtractors
    description = make_table_field_description(dee.event.description)
    application.update_field(
        document_type_id=dee.event.document_type_id,
        tenant_id=current_user_tenant,
        code=dee.event.code,
        description=description,
    )


@inject
def cloud_extractor_field_deleted(
    dee: DomainEventEnvelope[CloudExtractorFieldDeleted],
    application: DocumentTypeService = Provide[Containers.application.document_type],
    current_user_tenant: str = Provide[Containers.current_user_tenant],
) -> None:
    application.delete_fields(
        document_type_id=dee.event.document_type_id,
        tenant_id=current_user_tenant,
        field_codes=[dee.event.code],
    )


@inject
def perform_extraction_step_reply_handler(
    command_message: CommandMessage[PerformExtractionStepReply],
    application: DocumentTypeService = Provide[Containers.application.document_type],
) -> Optional[list[IMessage]]:
    command = command_message.command
    command_metadata = json.loads(command_message.message.headers[CommandMessageHeaders.METADATA])

    application.proceed_extraction_workflow(
        RawCommandReply(
            workflow_id=command_metadata["workflow_id"],
            step_id=command_metadata["step_id"],
            error=command.error_type,
            error_message=command.error_message,
        ),
    )


@inject
def extraction_fields_moved_handler(
    dee: DomainEventEnvelope[ExtractionFieldsMoved],
    application: DocumentTypeService = Provide[Containers.application.document_type],
    current_user_tenant: str = Provide[Containers.current_user_tenant],
) -> None:
    application.move_fields_between_extractors(
        document_type_id=dee.event.document_type_id,
        tenant_id=current_user_tenant,
        source_extractor_id=dee.event.source_extractor_id,
        target_extractor_id=dee.event.target_extractor_id,
        fields_codes=dee.event.fields_codes,
    )
