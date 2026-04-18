from http import HTTPStatus

from deps_extraction.constants import BASE_API_PREFIX, V2_PREFIX

ENDPOINT = BASE_API_PREFIX + V2_PREFIX + "/extracted-data"


def test_get_fields__edata_doesnt_exist__return_404(client):
    response = client.get(
        f"{ENDPOINT}/1/fields",
        params={"fieldCodes": ["code1"]},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_fields__field_codes_missing__return_422(client):
    response = client.get(f"{ENDPOINT}/1/fields")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_get_fields__fields_exist__return_matching_fields(client, saved_extracted_data):
    target_codes = [saved_extracted_data.fields[0].field_code, saved_extracted_data.fields[1].field_code]

    response = client.get(
        f"{ENDPOINT}/{saved_extracted_data.document_id}/fields",
        params={"fieldCodes": target_codes},
    )

    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert len(body) == 2
    returned_codes = {f["fieldCode"] for f in body}
    assert returned_codes == set(target_codes)
