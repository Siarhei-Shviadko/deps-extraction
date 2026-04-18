from typing import Any
from unittest import mock

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_extraction.application.document_type.interfaces import IDocumentTypeProxy
from deps_extraction.messaging.sagas import DocumentTypeCreationSaga
from deps_extraction.messaging.sagas_data import (
    DocumentTypeCreationSagaData,
    DocumentTypeCreationSteps,
)


@pytest.mark.document_type_creation_saga
def test_document_type_creation_saga(
    attach_extractor_request: dict[str, Any],
    document_type_creation_steps: DocumentTypeCreationSteps,
):
    document_type_creation_saga_data = DocumentTypeCreationSagaData(
        name=attach_extractor_request["name"],
        description=attach_extractor_request["description"],
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentTypeCreationSaga(steps=document_type_creation_steps),
            document_type_creation_saga_data,
        )
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert saga_data["name"] == attach_extractor_request["name"]
    assert saga_data["description"] == attach_extractor_request["description"]


@pytest.mark.document_type_creation_saga
def test_document_type_creation_saga_failed(
    attach_extractor_request: dict[str, Any],
    document_type_creation_steps: DocumentTypeCreationSteps,
    fake_document_type_proxy: IDocumentTypeProxy,
):
    document_type_creation_saga_data = DocumentTypeCreationSagaData(
        name=attach_extractor_request["name"],
        description=attach_extractor_request["description"],
    )

    document_type_creation_steps.create_new_document_type = mock.Mock(side_effect=RuntimeError())
    document_type_creation_steps.delete_document_type = mock.Mock()

    SagaUnitTestSupport.given().saga(
        DocumentTypeCreationSaga(steps=document_type_creation_steps),
        document_type_creation_saga_data,
    ).expect_rolled_back()

    document_type_creation_steps.delete_document_type.assert_called_once_with(document_type_creation_saga_data)
