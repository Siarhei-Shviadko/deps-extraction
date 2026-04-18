import logging

from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..sagas_data import DocumentTypeCreationSagaData, DocumentTypeCreationSteps

__all__ = ["DocumentTypeCreationSaga"]


class DocumentTypeCreationSaga(SimpleSaga[DocumentTypeCreationSagaData]):
    def __init__(self, steps: DocumentTypeCreationSteps) -> None:
        self._saga_definition = (
            self.step()
            .invoke_local(steps.create_document_type)
            .with_compensation(steps.delete_document_type)
            .step()
            .invoke_local(steps.create_new_document_type)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: DocumentTypeCreationSagaData) -> None:
        self._logger.info(
            "DocumentTypeCreationSaga: %s for document_type: %s is completed successfully",
            saga_id,
            data.name,
        )

    def on_saga_failed(self, saga_id: str, data: DocumentTypeCreationSagaData) -> None:
        self._logger.error("DocumentTypeCreationSaga: %s for document_type: %s is failed", saga_id, data.name)

    def on_saga_rolled_back(self, saga_id: str, data: DocumentTypeCreationSagaData) -> None:
        self._logger.error("DocumentTypeCreationSaga: %s for document_type: %s is rolled back", saga_id, data.name)
