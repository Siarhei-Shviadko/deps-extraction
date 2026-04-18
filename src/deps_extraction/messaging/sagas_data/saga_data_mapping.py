from deps_message_flow.sagas.orchestration import SagaDataMapping

from .document_type_creation import DocumentTypeCreationSagaData

__all__ = ["make_saga_data_mapping"]


def make_saga_data_mapping() -> SagaDataMapping:
    return SagaDataMapping(
        {
            DocumentTypeCreationSagaData.__name__: DocumentTypeCreationSagaData,
        },
    )
