import json
import random
import uuid
from http import HTTPStatus

import pytest
from deps_extracted_data.serializers.v1 import SerializedExtractedField

from deps_extraction.constants import API_PREFIX
from tests.data.chunked_data import corleone_table_dict_chunk_json, list_chunk_table
from tests.data.extracted_data import (
    kv_data_dict_only_key,
    kv_data_dict_only_value,
    string_data_dict_bbox_coordinates,
    table_data_dict_without_coordinates,
)
from tests.data.old_extracted_data import old_edata


class TestExtractedDataAPI:
    endpoint = API_PREFIX + "/extracted-data"

    def test_get_edata__edata_doesnt_exists__return_404(self, client):
        response = client.get(self.endpoint + "/1")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_edata__edata_exists__successful(self, client, extracted_data_factory, extracted_data_repository):
        edata = extracted_data_factory()
        extracted_data_repository.save(edata)

        response = client.get(f"{self.endpoint}/{edata.document_id}")

        assert response.status_code == HTTPStatus.OK

    def test_get_list_edata__edata_exists__successful(self, client, extracted_data_factory, extracted_data_repository):
        edata1 = extracted_data_factory(external_doc_id=random.randint(1, 10000))
        edata2 = extracted_data_factory(external_doc_id=random.randint(1, 10000))
        edata3 = extracted_data_factory(external_doc_id=random.randint(1, 10000))
        extracted_data_repository.save(edata1)
        extracted_data_repository.save(edata2)
        extracted_data_repository.save(edata3)

        response = client.get(f"{self.endpoint}", params={"documentIds": [edata1.document_id, edata2.document_id]})
        response2 = client.get(f"{self.endpoint}")

        assert response.status_code == HTTPStatus.OK
        assert response2.status_code == HTTPStatus.OK
        assert len(response.json()) == 2
        assert len(response2.json()) == 3

    def test_save_edata__valid_edata__successful(self, client, extracted_data_dict):
        response = client.put(f"{self.endpoint}/{random.randint(1, 10000)}", data=json.dumps(extracted_data_dict))
        assert response.status_code == HTTPStatus.OK

    def test_save_edata__invalid_table_cell_coordinates__error(
        self, client, extracted_data_table_field_with_invalid_cell_table_coordinates
    ):
        response = client.put(
            f"{self.endpoint}/{random.randint(1, 10000)}",
            data=json.dumps(extracted_data_table_field_with_invalid_cell_table_coordinates),
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_update_edata__valid_edata__successful(self, client, extracted_data_dict_with_several_fields):
        document_id = random.randint(1, 10000)
        edata = client.put(
            f"{self.endpoint}/{document_id}", data=json.dumps(extracted_data_dict_with_several_fields)
        ).json()

        field_to_update = edata[0]
        response = client.put(f"{self.endpoint}/{document_id}", data=json.dumps([field_to_update]))

        updated_field = next((field for field in response.json() if field["fieldPk"] == field_to_update["fieldPk"]))

        assert response.status_code == HTTPStatus.OK
        assert updated_field == field_to_update

    def test_delete_edata__edata_exists__successful(self, client, extracted_data_factory, extracted_data_repository):
        edata = extracted_data_factory()
        extracted_data_repository.save(edata)

        response = client.delete(f"{self.endpoint}/{edata.document_id}")

        assert response.status_code == HTTPStatus.OK
        assert client.get(f"{self.endpoint}/{edata.document_id}").status_code == HTTPStatus.NOT_FOUND

    def test_delete_edata__edata_doesnt_exist__no_errors(self, client):
        response = client.delete(f"{self.endpoint}/{random.randint(1, 10000)}")

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize(
        "broken_data",
        [table_data_dict_without_coordinates],
    )
    def test_save__broken_data__raise_error(self, client, broken_data):
        edata_dict = [{"fieldPk": uuid.uuid4().hex, "data": broken_data}]
        response = client.put(f"{self.endpoint}/{random.randint(1, 10000)}", data=json.dumps(edata_dict))

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("kv_pair", [kv_data_dict_only_key, kv_data_dict_only_value])
    def test_save__kv_pair_has_only_one_element__successful(self, client, kv_pair):
        field = {"fieldPk": uuid.uuid4().hex, "data": kv_pair}
        edata_dict = [field]
        response = client.put(f"{self.endpoint}/{random.randint(1, 10000)}", data=json.dumps(edata_dict))
        assert response.status_code == HTTPStatus.OK

    def test_add_extracted_data_field__valid_data__extracted_data_updated(
        self, client, extracted_data_factory, extracted_data_repository
    ):
        document_id = random.randint(1, 10000)
        edata = extracted_data_factory(external_doc_id=document_id)
        extracted_data_repository.save(edata)
        serialized = SerializedExtractedField.from_model(edata.fields[0])
        response = client.put(f"{self.endpoint}/{document_id}/field", data=serialized.json())
        assert response.status_code == HTTPStatus.OK
        assert SerializedExtractedField.parse_obj(response.json()).to_model() == edata.fields[0]

    def test_add_extracted_data_field__new_field_code__new_field_created(
        self, client, extracted_data_factory, extracted_data_repository
    ):
        document_id = random.randint(1, 10000)
        edata = extracted_data_factory(external_doc_id=document_id)
        initial_field_len = len(edata.fields)
        extracted_data_repository.save(edata)
        serialized = SerializedExtractedField.from_model(edata.fields[0])
        serialized_dict = serialized.dict(by_alias=True)
        serialized_dict["fieldPk"] = "Wrong Field Code"
        response = client.put(f"{self.endpoint}/{document_id}/field", json=serialized_dict)
        assert response.status_code == HTTPStatus.OK
        assert len(extracted_data_repository.find(document_id).fields) == initial_field_len + 1

    def test_delete_extracted_fields__extracted_fields_exist__successful(
        self, client, extracted_data_factory, extracted_data_repository
    ):
        edata = extracted_data_factory()
        extracted_data_repository.save(edata)

        fields_to_delete = [field.field_code for field in edata.fields]
        response = client.request(
            "DELETE", f"{self.endpoint}/{edata.document_id}/fields", data=json.dumps({"fieldPks": fields_to_delete})
        )

        assert response.status_code == HTTPStatus.OK

    def test_delete_extracted_fields__extracted_field_doesnt_exist__no_errors(
        self, client, extracted_data_factory, extracted_data_repository
    ):
        edata = extracted_data_factory()
        extracted_data_repository.save(edata)

        response = client.request(
            "DELETE",
            f"{self.endpoint}/{edata.document_id}/fields",
            data=json.dumps({"fieldPks": ["non_existing_code"]}),
        )

        assert response.status_code == HTTPStatus.OK

    def test_delete_extracted_fields__empty_codes_list__error(
        self, client, extracted_data_factory, extracted_data_repository
    ):
        edata = extracted_data_factory()
        extracted_data_repository.save(edata)

        response = client.request(
            "DELETE",
            f"{self.endpoint}/{edata.document_id}/fields",
            json=json.dumps({"fieldPks": []}),
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_save_edata__edata_without_id__successful__id_created(
        self, client, extracted_data_dict_with_fields_without_id
    ):
        response = client.put(f"{self.endpoint}/1", data=json.dumps(extracted_data_dict_with_fields_without_id))

        assert response.status_code == HTTPStatus.OK

        for i in range(4):
            assert response.json()[i]["data"]["id"] is not None

        for i in range(4, 8):
            for data in response.json()[i]["data"]:
                assert data["id"] is not None

    def test_save_old_edata__successful(self, client):
        response = client.put(f"{self.endpoint}/1", data=json.dumps(old_edata))
        old_edata_keys = {k for el in old_edata for k in el}

        assert response.status_code == HTTPStatus.OK
        assert len(old_edata_keys.difference({k for el in response.json() for k in el})) == 0
        for orig_edata, response_edata in zip(old_edata, response.json()):
            if isinstance(orig_edata["data"], list):
                continue
            orig_data_keys = {k for k in orig_edata["data"]}
            assert len(orig_data_keys.difference({k for k in response_edata["data"]})) == 0

    def test__save_extract_data__with_set_index__successful(
        self, client, extracted_data_dict_with_all_fields_and_set_indexes
    ):
        doc_id = random.randint(1, 10000)
        response = client.put(
            f"{self.endpoint}/{doc_id}", data=json.dumps(extracted_data_dict_with_all_fields_and_set_indexes)
        )

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "params",
        [
            ({"rowsPerChunk": 1}),
            ({"rowsPerChunk": 2}),
            ({"rowsPerChunk": 3}),
        ],
    )
    def test__get_paginated_extract_data_successful(self, client, params):
        doc_id = random.randint(1, 10000)
        edata = [
            list_chunk_table,
            {"fieldPk": "1", "data": string_data_dict_bbox_coordinates},
            corleone_table_dict_chunk_json[0],
        ]

        client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata))
        response = client.get(f"{self.endpoint}/{doc_id}", params=params)

        res_json = response.json()
        assert response.status_code == HTTPStatus.OK
        assert len(res_json) == 3
        assert res_json[1]["data"]["cells"] == []
        assert res_json[2]["data"][0]["cells"] == []
        assert res_json[2]["data"][1]["cells"] == []

    def test_get_paginated_extract_data__only_non_paginated_field__successful(self, client):
        doc_id = random.randint(1, 10000)
        edata = [{"fieldPk": uuid.uuid4().hex, "data": string_data_dict_bbox_coordinates}]
        client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata))

        response = client.get(f"{self.endpoint}/{doc_id}", params={"rowsPerChunk": 2})
        res_json = response.json()
        assert response.status_code == HTTPStatus.OK
        assert len(res_json) == 1

    def test_get_paginated_extract_data__only_paginated_field__successful(self, client):
        doc_id = random.randint(1, 10000)
        edata = [list_chunk_table, corleone_table_dict_chunk_json[0]]
        client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata))

        response = client.get(f"{self.endpoint}/{doc_id}", params={"rowsPerChunk": 2})
        res_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert len(res_json) == 2
        assert res_json[0]["data"]["cells"] == []
        assert res_json[1]["data"][0]["cells"] == []
        assert res_json[1]["data"][1]["cells"] == []

    @pytest.mark.aliases
    def test_get_edata__aliases_presents(
        self, client, empty_extracted_data, extracted_string_list_factory, extracted_data_repository
    ):
        empty_extracted_data.add_string_list(extracted_string_list_factory(with_aliases=True))
        extracted_data_repository.save(empty_extracted_data)
        response = client.get(f"{self.endpoint}/{empty_extracted_data.document_id}")

        assert response.status_code == HTTPStatus.OK
        assert "aliases" in response.json()[0] and response.json()[0]["aliases"] is not None

    @pytest.mark.aliases
    def test_get_edata__field_doesnt_support_aliases__alisases_doesnt_present(
        self, client, empty_extracted_data, extracted_string_factory_with_bbox_coord, extracted_data_repository
    ):
        empty_extracted_data.add_string_list(extracted_string_factory_with_bbox_coord())
        extracted_data_repository.save(empty_extracted_data)
        response = client.get(f"{self.endpoint}/{empty_extracted_data.document_id}")

        assert response.status_code == HTTPStatus.OK
        assert "aliases" not in response.json()[0] or response.json()[0]["aliases"] is None

    @pytest.mark.aliases
    def test_get_edata__aliases_correct_for_different_types_of_fields(
        self,
        client,
        empty_extracted_data,
        extracted_string_list_factory,
        extracted_data_repository,
        extracted_string_factory_with_bbox_coord,
    ):
        empty_extracted_data.add_string_list(extracted_string_list_factory(with_aliases=True))
        empty_extracted_data.add_string_list(extracted_string_factory_with_bbox_coord())
        extracted_data_repository.save(empty_extracted_data)
        response = client.get(f"{self.endpoint}/{empty_extracted_data.document_id}")

        assert response.status_code == HTTPStatus.OK
        for field in response.json():
            if isinstance(field["data"], list):
                assert "aliases" in field and field["aliases"] is not None
            else:
                assert "aliases" not in field or field["aliases"] is None

    @pytest.mark.aliases
    def test_save_edata__valid_edata_with_aliases__successful(
        self, client, extracted_data_dict_with_several_fields_and_aliases
    ):
        response = client.put(
            f"{self.endpoint}/{random.randint(1, 10000)}",
            data=json.dumps(extracted_data_dict_with_several_fields_and_aliases),
        )

        assert response.status_code == HTTPStatus.OK
        for el in response.json():
            if isinstance(el["data"], list):
                assert len(el["aliases"]) == len(el["data"])
            else:
                assert "aliases" not in el or el["aliases"] is None

    @pytest.mark.aliases
    def test_get_edata__with_aliases__ok(self, client, saved_extacted_data_with_with_aliases):
        response = client.get(f"{self.endpoint}/{saved_extacted_data_with_with_aliases.document_id}")

        assert response.status_code == HTTPStatus.OK
        assert "aliases" in response.json()[0] and response.json()[0]["aliases"] is not None
