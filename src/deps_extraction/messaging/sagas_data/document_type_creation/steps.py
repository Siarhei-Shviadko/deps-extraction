import logging

from deps_extraction.application.document_type.interfaces import IDocumentTypeProxy
from deps_extraction.application.document_type.service import DocumentTypeService
from deps_extraction.domain.exceptions import ExtractionException

from .saga_data import DocumentTypeCreationSagaData

__all__ = ["DocumentTypeCreationSteps"]


class DocumentTypeCreationSteps:
    def __init__(
        self,
        document_type_service: DocumentTypeService,
        document_type_proxy: IDocumentTypeProxy,
    ):
        self._document_type_service = document_type_service
        self._document_type_proxy = document_type_proxy

        self._logger = logging.getLogger(self.__class__.__name__)

    def create_document_type(self, data: DocumentTypeCreationSagaData) -> None:
        try:
            document_type_id = self._document_type_proxy.create_document_type(
                name=data.name,
                description=data.description,
            )
        except ExtractionException as exc:
            self._logger.error(f"Document type creation error. {str(exc)}", exc_info=True)
            raise
        except Exception as exc:
            self._logger.error(f"Unhandled error. {str(exc)}", exc_info=True)
            raise RuntimeError(str(exc))
        else:
            data.document_type_id = document_type_id

    def delete_document_type(self, data: DocumentTypeCreationSagaData) -> None:
        self._document_type_proxy.delete_document_type(data.document_type_id)

    def create_new_document_type(self, data: DocumentTypeCreationSagaData) -> None:
        self._document_type_service.save_document_type(
            document_type_id=data.document_type_id,
            tenant_id=data.tenant_id,
            name=data.name,
        )
