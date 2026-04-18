from http import HTTPStatus

import pytest

from deps_extraction.constants import API_PREFIX
from deps_extraction.domain.model import ExtractionType


@pytest.mark.document_type
def test_get_document_types__ok(
    fake_document_type_repository,
    test_document_type_with_llm_and_plugin_extractors_with_fields,
    client,
):
    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors_with_fields)
    response = client.get(url=f"{API_PREFIX}/document-types")

    assert response.status_code == HTTPStatus.OK

    json_response = response.json()

    assert json_response["result"]
    assert len(json_response["result"]) == 1

    if test_document_type_with_llm_and_plugin_extractors_with_fields.extraction_type != ExtractionType.NON:
        extracion_type = test_document_type_with_llm_and_plugin_extractors_with_fields.extraction_type
    else:
        extracion_type = None

    assert json_response["result"][0]["id"] == test_document_type_with_llm_and_plugin_extractors_with_fields.id()
    assert (
        json_response["result"][0]["tenantId"]
        == test_document_type_with_llm_and_plugin_extractors_with_fields.tenant_id()
    )
    assert (
        json_response["result"][0]["documentType"] == test_document_type_with_llm_and_plugin_extractors_with_fields.name
    )
    assert json_response["result"][0]["extractorType"] == extracion_type
    assert json_response["result"][0]["fields"]


@pytest.mark.document_type
def test_get_document_type__ok(
    fake_document_type_repository,
    test_document_type,
    test_id,
    client,
):
    fake_document_type_repository.save(test_document_type)
    response = client.get(url=f"{API_PREFIX}/document-types/{test_id}")

    assert response.status_code == HTTPStatus.OK

    json_response = response.json()

    extraction_type = (
        None if test_document_type.extraction_type == ExtractionType.NON else test_document_type.extraction_type
    )

    assert json_response["id"] == test_document_type.id()
    assert json_response["tenantId"] == test_document_type.tenant_id()
    assert json_response["documentType"] == test_document_type.name
    assert json_response["extractorType"] == extraction_type
