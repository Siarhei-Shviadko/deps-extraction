import logging
from typing import Optional

from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.sagas.orchestration import Saga, SagaInstanceFactory

from deps_extraction.domain.interfaces import IDocumentTypeRepository
from deps_extraction.domain.model import (
    AttachmentInfo,
    DocumentType,
    ExtractorType,
    FieldAttachment,
)
from deps_extraction.extras.datasource.backoff import retry_transaction
from deps_extraction.messaging.sagas import DocumentTypeCreationSaga
from deps_extraction.messaging.sagas_data import DocumentTypeCreationSagaData

__all__ = ["AttachmentService"]


class AttachmentService:
    EXTRACTOR_AGGREGATE = "Extractor"

    def __init__(
        self,
        document_type_repository: IDocumentTypeRepository,
        domain_event_publisher: DomainEventPublisher,
        saga_instance_factory: SagaInstanceFactory,
        sagas: list[Saga],
    ) -> None:
        self._document_type_repository = document_type_repository
        self._domain_event_publisher = domain_event_publisher

        self._sagas = {saga.__class__: saga for saga in sagas}
        self._saga_instance_factory = saga_instance_factory

        self._logger = logging.getLogger(self.__class__.__name__)

    @retry_transaction()
    def attach_extractor(
        self,
        document_type_name: str,
        tenant_id: str,
        extractor_type: Optional[ExtractorType],
        fields: list[FieldAttachment],
        description: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        extractor_id: Optional[str] = None,
        image_transformations: Optional[list[str]] = None,
    ) -> AttachmentInfo:
        with self._document_type_repository.repeatable_read():
            document_type = self._document_type_repository.find_by_name_for_tenant(
                document_type_name=document_type_name,
                tenant_id=tenant_id,
            )
            if document_type is None:
                document_type_id = self._start_document_type_creation_saga(
                    name=document_type_name,
                    description=description,
                )
                document_type = self._document_type_repository.get(document_type_id=document_type_id)

            return self.perform_attachment(
                document_type=document_type,
                extractor_type=extractor_type,
                fields=fields,
                description=description,
                engine=engine,
                language=language,
                image_transformations=image_transformations,
                extractor_id=extractor_id,
            )

    def perform_attachment(
        self,
        document_type: DocumentType,
        extractor_type: Optional[ExtractorType],
        fields: list[FieldAttachment],
        description: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        extractor_id: Optional[str] = None,
        image_transformations: Optional[list[str]] = None,
    ) -> AttachmentInfo:
        if extractor_type is not None:
            extractor = document_type.attach_extractor(
                type_=extractor_type,
                fields=fields,
                description=description,
                engine=engine,
                language=language,
                image_transformations=image_transformations,
                extractor_id=extractor_id,
            )

            self._document_type_repository.save(document_type)
            self._publish_events(document_type)

        return AttachmentInfo(
            document_type.command_channel,
            document_type_id=document_type.id(),
            extractor_id=extractor.id() if extractor_type else None,
        )

    def _start_document_type_creation_saga(self, name: str, description: Optional[str] = None) -> str:
        document_type_creation_saga_data = DocumentTypeCreationSagaData(name=name, description=description)

        si = self._saga_instance_factory.create(
            self._sagas[DocumentTypeCreationSaga],
            document_type_creation_saga_data,
        )

        self._logger.info("Saga %s for document_type creation is created", si.saga_id)

        return document_type_creation_saga_data.document_type_id

    def _publish_events(self, document_type: DocumentType) -> None:
        self._domain_event_publisher.publish(
            self.EXTRACTOR_AGGREGATE,
            str(document_type.id),
            document_type.events,
        )
