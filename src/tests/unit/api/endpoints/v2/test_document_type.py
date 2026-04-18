from http import HTTPStatus
from typing import Any

import pytest
from starlette.testclient import TestClient

from deps_extraction.constants import BASE_API_PREFIX, V2_PREFIX
from deps_extraction.domain.exceptions import AttachmentExtractorConflict
from deps_extraction.domain.interfaces import IDocumentTypeRepository
from deps_extraction.domain.model import AttachmentInfo, ExtractorType


@pytest.mark.document_type
def test_create_field__document_type_doesnt_exist__not_found(client, test_id, create_field_request):
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_id}/extraction-fields"

    response = client.post(url=url, json=create_field_request)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.document_type
def test_create_field__document_type_exists__created(
    fake_document_type_repository: IDocumentTypeRepository,
    create_field_with_request_2,
    test_document_type_with_llm_extractors,
    test_id,
    client,
):
    fake_document_type_repository.save(test_document_type_with_llm_extractors)
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_id}/extraction-fields"

    extractor_id = next(
        (e for e in test_document_type_with_llm_extractors.extractors.values() if e.type == ExtractorType.LLM)
    ).id()
    payload = create_field_with_request_2 | {"extractor_id": extractor_id}

    response = client.post(url=url, json=payload)

    assert response.status_code == HTTPStatus.CREATED
    json_response = response.json()
    assert json_response["code"]
    assert json_response["required"] == create_field_with_request_2["required"]
    assert json_response["fieldType"] == create_field_with_request_2["type"]
    assert json_response["confidential"] == create_field_with_request_2["confidential"]
    assert json_response["readOnly"] == create_field_with_request_2["read_only"]
    assert json_response["order"] == create_field_with_request_2["order"]


@pytest.mark.document_type
def test_create_field__document_type_exists__created__with_code(
    fake_document_type_repository: IDocumentTypeRepository,
    create_field_with_request_2,
    test_document_type_with_llm_extractors,
    test_id,
    client,
):
    fake_document_type_repository.save(test_document_type_with_llm_extractors)
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_id}/extraction-fields"

    extractor_id = next(
        (e for e in test_document_type_with_llm_extractors.extractors.values() if e.type == ExtractorType.LLM)
    ).id()
    payload = create_field_with_request_2 | {"extractor_id": extractor_id, "code": "new_field"}

    response = client.post(url=url, json=payload)

    assert response.status_code == HTTPStatus.CREATED
    json_response = response.json()
    assert json_response["code"]
    assert json_response["required"] == create_field_with_request_2["required"]
    assert json_response["fieldType"] == create_field_with_request_2["type"]
    assert json_response["confidential"] == create_field_with_request_2["confidential"]
    assert json_response["readOnly"] == create_field_with_request_2["read_only"]
    assert json_response["order"] == create_field_with_request_2["order"]
    assert json_response["code"] == "new_field"


@pytest.mark.document_type
def test_create_field__invalid_list_dict_base_type_meta__error(
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type_with_llm_extractors,
    test_id,
    client,
):
    fake_document_type_repository.save(test_document_type_with_llm_extractors)
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_id}/extraction-fields"

    extractor_id = next(
        (e for e in test_document_type_with_llm_extractors.extractors.values() if e.type == ExtractorType.LLM)
    ).id()
    payload = {
        "name": "test name",
        "type": "list",
        "description": {
            "baseType": "dict",
            "baseTypeMeta": {},
        },
        "required": True,
        "extractorId": extractor_id,
        "code": "test_code",
    }

    response = client.post(url=url, json=payload)

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.document_type
def test_update_field__document_type_not_exist__not_found(client, test_id):
    test_field_code = "Not existed code"
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_id}/extraction-fields/{test_field_code}"

    response = client.patch(url=url, json={"name": "test name"})

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.document_type
def test_update_field__field_not_exist__not_found(
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type,
    test_id,
    client,
):
    fake_document_type_repository.save(test_document_type)
    test_field_code = "Not existed code"
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_id}/extraction-fields/{test_field_code}"

    response = client.patch(url=url, json={"name": "test name"})

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.document_type
def test_update_field__field_exist__updated(
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type_with_llm_and_plugin_extractors_with_fields,
    update_field_request,
    client,
):
    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors_with_fields)

    test_field_code = test_document_type_with_llm_and_plugin_extractors_with_fields.extraction_fields[0].code()
    test_document_type_id = test_document_type_with_llm_and_plugin_extractors_with_fields.id()
    extractor_id: str = next(
        iter(test_document_type_with_llm_and_plugin_extractors_with_fields.extractors.values())
    ).id()
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_document_type_id}/extraction-fields/{test_field_code}"

    response = client.patch(url=url, json=update_field_request, params={"extractorId": extractor_id})

    assert response.status_code == HTTPStatus.OK

    updated_field = response.json()

    assert updated_field["code"] == test_field_code
    assert updated_field["name"] == update_field_request["name"]

    assert updated_field["required"] == update_field_request["required"]
    assert updated_field["confidential"] == update_field_request["confidential"]
    assert updated_field["readOnly"] == update_field_request["read_only"]
    assert (
        updated_field["fieldType"]
        == test_document_type_with_llm_and_plugin_extractors_with_fields.extraction_fields[0].profile.type
    )


def test_delete_fields__document_type_doesnt_exist__no_error(client, test_id):
    response = client.delete(
        f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_id}/extraction-fields",
        params={"fieldCodes": "test_field_code"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_fields__document_type_exist__deleted(
    client,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type_plugin_extractor_with_field,
):
    fake_document_type_repository.save(document_type=test_document_type_plugin_extractor_with_field)
    field_code = test_document_type_plugin_extractor_with_field.composite_fields[0].code()

    response = client.delete(
        f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_document_type_plugin_extractor_with_field.id()}/extraction-fields",
        params={"fieldCodes": [field_code]},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    document_type = fake_document_type_repository.find_by_id_for_tenant(
        test_document_type_plugin_extractor_with_field.id(), test_document_type_plugin_extractor_with_field.tenant_id()
    )
    assert document_type.composite_fields == []


@pytest.mark.document_type
def test_attach_extractor__created(
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    test_id: str,
    test_tenant: str,
    client: TestClient,
    attachment_service_service_mock,
    attachment_info: AttachmentInfo,
):
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/attach-extractor"
    attachment_service_service_mock.attach_extractor.return_value = attachment_info

    response = client.post(url=url, json=attach_extractor_request)

    assert response.status_code == HTTPStatus.CREATED

    attachment_service_service_mock.attach_extractor.assert_called_once_with(
        document_type_name=attach_extractor_request["name"],
        tenant_id=test_tenant,
        extractor_type=attach_extractor_request["extractorType"],
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        extractor_id=None,
        fields=[],
    )

    json_response = response.json()

    assert json_response["command_channel"]
    assert json_response["documentTypeId"]
    assert json_response["extractorId"]


@pytest.mark.document_type
def test_attach_extractor_with_name__created(
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    test_id: str,
    test_tenant: str,
    client: TestClient,
    attachment_service_service_mock,
    attachment_info: AttachmentInfo,
):
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/attach-extractor"
    attachment_service_service_mock.attach_extractor.return_value = attachment_info

    response = client.post(url=url, json=attach_extractor_request)

    assert response.status_code == HTTPStatus.CREATED

    attachment_service_service_mock.attach_extractor.assert_called_once_with(
        document_type_name=attach_extractor_request["name"],
        tenant_id=test_tenant,
        extractor_type=attach_extractor_request["extractorType"],
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        extractor_id=None,
        fields=[],
    )

    json_response = response.json()

    assert json_response["command_channel"]
    assert json_response["documentTypeId"]


@pytest.mark.document_type
def test_attach_extractor__with_extractor_id__created(
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    test_id: str,
    test_tenant: str,
    client: TestClient,
    attachment_service_service_mock,
    attachment_info: AttachmentInfo,
):
    attach_extractor_request["extractorId"] = "new_extractor_id"
    attachment_info.extractor_id = "new_extractor_id"

    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/attach-extractor"
    attachment_service_service_mock.attach_extractor.return_value = attachment_info

    response = client.post(url=url, json=attach_extractor_request)

    assert response.status_code == HTTPStatus.CREATED

    attachment_service_service_mock.attach_extractor.assert_called_once_with(
        document_type_name=attach_extractor_request["name"],
        tenant_id=test_tenant,
        extractor_type=attach_extractor_request["extractorType"],
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        extractor_id=attach_extractor_request["extractorId"],
        fields=[],
    )

    json_response = response.json()

    assert json_response["command_channel"]
    assert json_response["documentTypeId"]
    assert json_response["extractorId"] == "new_extractor_id"


@pytest.mark.document_type
def test_attach_extractor__conflict(
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    client: TestClient,
    attachment_service_service_mock,
):
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/attach-extractor"
    attachment_service_service_mock.attach_extractor.side_effect = AttachmentExtractorConflict(
        document_type=attach_extractor_request["name"],
        new_extractor=attach_extractor_request["extractorType"],
        previous_extractor=attach_extractor_request["extractorType"],
    )

    response = client.post(url=url, json=attach_extractor_request)

    assert response.status_code == HTTPStatus.CONFLICT


def test_detach_extractor__ok(
    client: TestClient,
    fake_document_type_repository,
    test_document_type_with_llm_and_plugin_extractors,
):
    assert len(test_document_type_with_llm_and_plugin_extractors.extractors) == 2

    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)
    target_extractor_id = list(test_document_type_with_llm_and_plugin_extractors.extractors.values())[0].id()
    target_doc_type_id = test_document_type_with_llm_and_plugin_extractors.id()
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{target_doc_type_id}/extractors/{target_extractor_id}"

    response = client.delete(url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    updated_doc = fake_document_type_repository.get(target_doc_type_id)
    assert len(updated_doc.extractors) == 1


def test_detach_extractor__fake_doc__no_errors(
    client: TestClient,
    fake_document_type_repository,
    test_document_type_with_llm_and_plugin_extractors,
):
    assert len(test_document_type_with_llm_and_plugin_extractors.extractors) == 2

    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)
    target_doc_type_id = test_document_type_with_llm_and_plugin_extractors.id()
    target_extractor_id = list(test_document_type_with_llm_and_plugin_extractors.extractors.values())[0].id()
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/fake_doc_id/extractors/{target_extractor_id}"

    response = client.delete(url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    updated_doc = fake_document_type_repository.get(target_doc_type_id)
    assert len(updated_doc.extractors) == 2


def test_detach_extractor__fake_extractor__no_errors(
    client: TestClient,
    fake_document_type_repository,
    test_document_type_with_llm_and_plugin_extractors,
):
    assert len(test_document_type_with_llm_and_plugin_extractors.extractors) == 2

    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)
    target_doc_type_id = test_document_type_with_llm_and_plugin_extractors.id()
    target_extractor_id = list(test_document_type_with_llm_and_plugin_extractors.extractors.values())[0].id()
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{target_doc_type_id}/extractors/fake_id"

    response = client.delete(url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    updated_doc = fake_document_type_repository.get(target_doc_type_id)
    assert len(updated_doc.extractors) == 2


def test_detach_extractor__not_llm_extractor__error(
    client: TestClient,
    fake_document_type_repository,
    test_document_type_with_llm_and_plugin_extractors,
):
    assert len(test_document_type_with_llm_and_plugin_extractors.extractors) == 2

    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)
    target_doc_type_id = test_document_type_with_llm_and_plugin_extractors.id()
    target_extractor_id = list(test_document_type_with_llm_and_plugin_extractors.extractors.values())[1].id()
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{target_doc_type_id}/extractors/{target_extractor_id}"

    response = client.delete(url)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    updated_doc = fake_document_type_repository.get(target_doc_type_id)
    assert len(updated_doc.extractors) == 2


@pytest.mark.document_type
def test_attach_extractor__only_name__created(
    fake_document_type_repository: IDocumentTypeRepository,
    client: TestClient,
    attachment_service_service_mock,
    attachment_info,
):
    attachment_info.extractor_id = None
    attachment_service_service_mock.attach_extractor.return_value = attachment_info
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/attach-extractor"

    response = client.post(url=url, json={"name": "test_name"})

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["extractorId"] is None


@pytest.mark.document_type
def test_update_fields__field_not_exist__not_found(
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type,
    test_id,
    client,
):
    fake_document_type_repository.save(test_document_type)
    test_field_code = "Not existed code"
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_id}/extraction-fields"

    response = client.patch(url=url, json={"fields": [{"code": test_field_code, "name": "test name"}]})

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.document_type
def test_update_fields__field_exist__updated(
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type_plugin_extractor_with_field,
    update_field_request,
    client,
):
    fake_document_type_repository.save(test_document_type_plugin_extractor_with_field)

    test_field_code = test_document_type_plugin_extractor_with_field.extraction_fields[0].code()
    test_document_type_id = test_document_type_plugin_extractor_with_field.id()
    url = f"{BASE_API_PREFIX}{V2_PREFIX}/document-types/{test_document_type_id}/extraction-fields"

    update_field_request["code"] = test_field_code
    response = client.patch(url=url, json={"fields": [update_field_request]})

    assert response.status_code == HTTPStatus.OK

    updated_fields = response.json()["fields"]

    assert updated_fields[0]["code"] == test_field_code
    assert updated_fields[0]["name"] == update_field_request["name"]

    assert updated_fields[0]["required"] == update_field_request["required"]
    assert updated_fields[0]["confidential"] == update_field_request["confidential"]
    assert updated_fields[0]["readOnly"] == update_field_request["read_only"]
    assert (
        updated_fields[0]["fieldType"]
        == test_document_type_plugin_extractor_with_field.extraction_fields[0].profile.type
    )


def test_create_field_for_llm_extractor__id_not_provided__error():
    ...
