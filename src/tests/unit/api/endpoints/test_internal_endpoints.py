from http import HTTPStatus

from deps_extraction import constants

endpoint = constants.BASE_API_PREFIX
internal_endpoint = constants.INTERNAL_API_PREFIX


def test_get_all_extraction_fields(
    client,
    fake_document_type_repository,
    test_document_type_with_llm_and_plugin_extractors_with_fields,
):
    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors_with_fields)
    response = client.get(f"{internal_endpoint}/fields")

    assert response.status_code == HTTPStatus.OK
    assert response.json()


def test_internal_api_not_in_openapi(client):
    response = client.get(f"{endpoint}/v1/openapi.json")

    assert response.status_code == HTTPStatus.OK
    response_json = response.json()

    for path in response_json["paths"]:
        assert not path.startswith(internal_endpoint)
