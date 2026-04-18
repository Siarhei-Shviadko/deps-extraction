import pytest

from deps_extraction.application.document_type import DocumentTypeService
from deps_extraction.application.document_type.interfaces import IDocumentTypeProxy
from deps_extraction.messaging.sagas_data import DocumentTypeCreationSteps


@pytest.fixture
def document_type_creation_steps(
    fake_document_type_proxy: IDocumentTypeProxy,
    document_type_service: DocumentTypeService,
):
    return DocumentTypeCreationSteps(
        document_type_service=document_type_service,
        document_type_proxy=fake_document_type_proxy,
    )
