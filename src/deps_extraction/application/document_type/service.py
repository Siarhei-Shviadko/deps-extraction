import logging
from contextlib import suppress
from itertools import chain
from typing import Any, Optional

from deps_extracted_data.model import ExtractedDataFactory
from deps_extracted_data.model.extracted_data import ExtractedData
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher

from deps_extraction.constants import COMMANDS_CHANNEL, COMMANDS_REPLIES_CHANNEL
from deps_extraction.domain.events import GetDocumentTypes
from deps_extraction.domain.exceptions import (
    DocumentTypeNotFound,
    ExtractedDataNotFound,
    ExtractionWorkflowNotFoundError,
    ExtractorNotFound,
    InconsistentProfileDescription,
)
from deps_extraction.domain.interfaces import (
    IDocumentTypeRepository,
    IExtractedDataRepository,
    IExtractionWorkflowRepository,
)
from deps_extraction.domain.model import (
    CompositeField,
    DocumentType,
    DocumentTypeFactory,
    ExtractionFieldData,
    FieldDescription,
    FieldType,
    RawDocumentType,
    RawUpdateField,
)
from deps_extraction.domain.types import RawCommand, RawCommandReply
from deps_extraction.extras.datasource.backoff import retry_transaction

__all__ = ["DocumentTypeService"]


class DocumentTypeService:
    EXTRACTOR_AGGREGATE = "Extractor"

    def __init__(
        self,
        command_producer: CommandProducer,
        domain_event_publisher: DomainEventPublisher,
        document_type_repository: IDocumentTypeRepository,
        extracted_data_repository: IExtractedDataRepository,
        extraction_workflow_repository: IExtractionWorkflowRepository,
    ) -> None:
        self._command_producer = command_producer
        self._domain_event_publisher = domain_event_publisher
        self._document_type_repository = document_type_repository
        self._extracted_data_repository = extracted_data_repository
        self._extraction_workflow_repository = extraction_workflow_repository

        self._document_type_factory = DocumentTypeFactory
        self._logger = logging.getLogger(self.__class__.__name__)

    def initialize(self):
        self._command_producer.send(
            COMMANDS_CHANNEL,
            GetDocumentTypes(),
            COMMANDS_REPLIES_CHANNEL,
        )

    def extract_document(
        self,
        document_id: str,
        document_type_id: str,
        tenant_id: str,
        correlation_headers: dict[str, Any],
        extra_headers: dict[str, Any],
        template_version_id: Optional[str] = None,
        language: Optional[str] = None,
        engine: Optional[str] = None,
        llm_type: Optional[str] = None,
    ) -> None:
        document_type = self.get_document_type(document_type_id=document_type_id, tenant_id=tenant_id)

        workflow = document_type.create_workflow_for(
            document_id=document_id,
            tenant_id=document_type.tenant_id(),
            correlation_headers=correlation_headers,
            extra_headers=extra_headers,
            template_version_id=template_version_id,
            language=language,
            engine=engine,
            llm_type=llm_type,
        )
        self._extraction_workflow_repository.save(workflow)

        initial_command = workflow.start_workflow()

        self._logger.info("Start ExtractionWorkflow: %s, with initial command: %s", workflow.id(), initial_command)

        self._send_workflow_command(initial_command)

    def save_new_document_type(self, document_type_id: str, tenant_id: str, name: str) -> None:
        document_type = self._document_type_factory.create(tenant_id=tenant_id, name=name, id_=document_type_id)
        self._document_type_repository.save_new(document_type)

    def save_document_type(
        self,
        document_type_id: str,
        tenant_id: str,
        name: str,
    ) -> None:
        document_type = self._document_type_factory.create(
            tenant_id=tenant_id,
            name=name,
            id_=document_type_id,
        )

        self._document_type_repository.save(document_type)
        self._publish_events(document_type)

    def save_new_document_types(self, raw_document_types: list[RawDocumentType]) -> None:
        document_types: list[DocumentType] = []

        for raw_dt in raw_document_types:
            try:
                document_types.append(
                    self._document_type_factory.create(
                        tenant_id=raw_dt["tenant_id"],
                        name=raw_dt["name"],
                        id_=raw_dt["document_type_id"],
                        extraction_type=raw_dt["extraction_type"],
                    ),
                )
            except InconsistentProfileDescription:
                self._logger.error(
                    f"Failed to save document type {raw_dt['document_type_id']}. Inconsistent field description",
                )
            except Exception as e:
                self._logger.error(f"Failed to save document type {raw_dt['document_type_id']}. {e}")

        self._document_type_repository.save_new_all(document_types)

    def delete_document_type(self, document_type_id: str, tenant_id: str) -> None:
        document_type = self._document_type_repository.find_by_id_for_tenant(
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )

        self._document_type_repository.delete(document_type)

    def get_document_types(self, tenant_id: str) -> list[DocumentType]:
        return self._document_type_repository.find_by_tenant(tenant_id=tenant_id)

    def get_document_type(self, document_type_id: str, tenant_id: str) -> DocumentType:
        return self._document_type_repository.find_by_id_for_tenant(
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )

    @retry_transaction()
    def create_field(
        self,
        document_type_id: str,
        tenant_id: str,
        name: str,
        type_: FieldType,
        required: bool,
        order: int,
        description: Optional[FieldDescription] = None,
        code: Optional[str] = None,
        confidential: Optional[bool] = None,
        read_only: Optional[bool] = None,
        extractor_id: Optional[str] = None,
    ) -> CompositeField:
        with self._document_type_repository.repeatable_read():
            document_type = self._document_type_repository.find_by_id_for_tenant(
                document_type_id=document_type_id,
                tenant_id=tenant_id,
            )

            created_field = document_type.add_field(
                code=code,
                name=name,
                type_=type_,
                required=required,
                description=description,
                confidential=confidential,
                read_only=read_only,
                order=order,
                extractor_id=extractor_id,
            )
            self._document_type_repository.save(document_type)

        self._publish_events(document_type)

        return created_field

    @retry_transaction()
    def update_field(
        self,
        document_type_id: str,
        tenant_id: str,
        code: str,
        name: Optional[str] = None,
        required: Optional[bool] = None,
        confidential: Optional[bool] = None,
        read_only: Optional[bool] = None,
        description: Optional[FieldDescription] = None,
        order: Optional[int] = None,
        extractor_id: Optional[str] = None,
    ) -> CompositeField:
        with self._document_type_repository.repeatable_read():
            document_type = self._document_type_repository.find_by_id_for_tenant(
                document_type_id=document_type_id,
                tenant_id=tenant_id,
            )
            updated_field = document_type.update_field(
                code=code,
                name=name,
                required=required,
                read_only=read_only,
                confidential=confidential,
                description=description,
                order=order,
                extractor_id=extractor_id,
            )
            self._document_type_repository.save(document_type)

        self._publish_events(document_type)

        return updated_field

    def update_fields(
        self,
        document_type_id: str,
        tenant_id: str,
        fields: list[RawUpdateField],
    ) -> list[CompositeField]:
        document_type = self._document_type_repository.find_by_id_for_tenant(
            document_type_id=document_type_id,
            tenant_id=tenant_id,
        )
        updated_fields = document_type.update_fields(fields)

        self._document_type_repository.save(document_type)
        self._publish_events(document_type)

        return updated_fields

    def delete_fields(self, document_type_id: str, tenant_id: str, field_codes: list[str]) -> None:
        document_type = self.get_document_type(document_type_id=document_type_id, tenant_id=tenant_id)
        document_type.delete_fields(field_codes)

        self._document_type_repository.save(document_type)
        self._publish_events(document_type)

    def copy_fields(self, tenant_id: str, source_document_type_id: str, target_document_type_id: str) -> None:
        source_document_type = self._document_type_repository.find_by_id_for_tenant(
            document_type_id=source_document_type_id,
            tenant_id=tenant_id,
        )
        target_document_type = self._document_type_repository.find_by_id_for_tenant(
            document_type_id=target_document_type_id,
            tenant_id=tenant_id,
        )
        target_document_type.copy_fields_from(source_document_type)

        self._document_type_repository.save(target_document_type)
        self._publish_events(target_document_type)

    def detach_extractor(
        self,
        document_type_id: str,
        extractor_id: str,
        tenant_id: str,
    ) -> None:
        with suppress(DocumentTypeNotFound, ExtractorNotFound):
            document_type = self.get_document_type(document_type_id=document_type_id, tenant_id=tenant_id)
            document_type.detach_extractor(extractor_id=extractor_id)
            self._document_type_repository.save(document_type)

            self._publish_events(document_type)

    def proceed_extraction_workflow(self, reply: RawCommandReply) -> None:
        if not (workflow := self._extraction_workflow_repository.get(id_=reply["workflow_id"])):
            raise ExtractionWorkflowNotFoundError(f"Workflow with id: {reply['workflow_id']} doens't exist.")

        next_command = workflow.iter_workflow(reply)
        self._extraction_workflow_repository.save(workflow)

        self._send_workflow_command(next_command)

    def move_fields_between_extractors(
        self,
        document_type_id: str,
        tenant_id: str,
        source_extractor_id: str,
        target_extractor_id: str,
        fields_codes: list[str],
    ) -> None:
        document_type = self.get_document_type(document_type_id=document_type_id, tenant_id=tenant_id)

        document_type.move_fields_between_extractors(source_extractor_id, target_extractor_id, fields_codes)

        self._document_type_repository.save(document_type)

    def get_all_extraction_fields(self) -> list[ExtractionFieldData]:
        document_types = self._document_type_repository.find_all()

        return list(chain.from_iterable(dt.extraction_fields_data for dt in document_types))

    def _find_or_create_extracted_data(self, document_id: int) -> ExtractedData:
        try:
            extracted_data = self._extracted_data_repository.find(document_id)
        except ExtractedDataNotFound:
            extracted_data = ExtractedDataFactory.make_extracted_data(document_id=document_id)

        return extracted_data

    def _publish_events(self, document_type: DocumentType) -> None:
        self._domain_event_publisher.publish(
            self.EXTRACTOR_AGGREGATE,
            document_type.id(),
            document_type.events,
        )

    def _send_workflow_command(self, command: RawCommand) -> None:
        self._command_producer.send(
            channel=command["channel"],
            command=command["command"],
            reply_to=command["reply_to"],
            headers=command["headers"],
        )
