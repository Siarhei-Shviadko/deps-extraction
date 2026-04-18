import copy
import json
import random
import uuid
from http import HTTPStatus
from uuid import uuid4

import pytest

from deps_extraction.constants import BASE_API_PREFIX, V2_PREFIX
from deps_extraction.infrastructure.data_object_accessors.context_vars import user
from deps_extraction.infrastructure.repositories.extracted_data.types import (
    CommonDictType,
)
from tests.data.chunked_data import corleone_table_dict_chunk_json, list_chunk_table
from tests.data.extracted_data import (
    kv_data_dict_only_key,
    kv_data_dict_only_value,
    list_string_data_dict,
    string_data_dict_bbox_coordinates,
    table_chunked_data_dict_bbox_coordinates,
    table_chunked_data_dict_table_coordinates,
    table_chunked_data_dict_text_coordinates,
    table_data_dict_without_coordinates,
    table_info_dict_bbox_coordinates,
    table_info_dict_bbox_coordinates_list_of_tables_with_aliases,
    table_info_dict_bbox_coordinates_list_of_tables_without_aliases,
    table_info_dict_table_coordinates,
)


@pytest.fixture(
    params=[
        table_chunked_data_dict_bbox_coordinates,
        table_chunked_data_dict_table_coordinates,
        table_chunked_data_dict_text_coordinates,
    ],
)
def chunked_data(request):
    return request.param


@pytest.fixture(
    params=[
        table_info_dict_bbox_coordinates,
        table_info_dict_table_coordinates,
        table_info_dict_bbox_coordinates_list_of_tables_with_aliases,
        table_info_dict_bbox_coordinates_list_of_tables_without_aliases,
    ],
)
def table_info(request):
    return request.param


@pytest.fixture()
def table_info_and_data(table_info, chunked_data):
    chunked_data["listIndex"] = table_info["listIndex"]
    return {"table_info": table_info, "chunked_data": chunked_data}


@pytest.fixture
def list_chunk_table_without_ids_in_cells():
    field = copy.deepcopy(list_chunk_table)
    for el in field["data"]:
        for cell in el["cells"]:
            cell.pop("pk")
    return field


class TestExtractedDataAPI:
    endpoint = BASE_API_PREFIX + V2_PREFIX + "/extracted-data"

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

    def test_save_edata__valid_edata__successful(self, client, extracted_data_dict_v2):
        response = client.put(f"{self.endpoint}/{random.randint(1, 10000)}", data=json.dumps(extracted_data_dict_v2))
        assert response.status_code == HTTPStatus.OK

    def test_update_edata__valid_edata__successful(self, client, extracted_data_dict_with_several_fields_v2):
        document_id = random.randint(1, 10000)
        edata = client.put(
            f"{self.endpoint}/{document_id}", data=json.dumps(extracted_data_dict_with_several_fields_v2)
        ).json()

        field_to_update = edata["fields"][0]
        edata["fields"] = [field_to_update]

        response = client.put(f"{self.endpoint}/{document_id}", data=json.dumps(edata))
        updated_fields = response.json()["fields"]
        updated_field = next((field for field in updated_fields if field["fieldCode"] == field_to_update["fieldCode"]))

        assert response.status_code == HTTPStatus.OK
        assert updated_field == field_to_update

    def test_update_edata_override_fields__valid_edata__successful(
        self, client, extracted_data_dict_with_several_fields_v2
    ):
        document_id = random.randint(1, 10000)
        edata = client.put(
            f"{self.endpoint}/{document_id}", data=json.dumps(extracted_data_dict_with_several_fields_v2)
        ).json()

        edata["fields"] = edata["fields"][:1]

        response = client.put(f"{self.endpoint}/{document_id}/override", data=json.dumps(edata))

        assert response.status_code == HTTPStatus.OK
        assert response.json() == edata

    @pytest.mark.parametrize(
        "broken_data",
        [table_data_dict_without_coordinates],
    )
    def test_save__broken_data__raise_error(self, client, broken_data):
        edata_dict = [{"fieldCode": uuid4().hex, "data": broken_data}]
        response = client.put(f"{self.endpoint}/{random.randint(1, 10000)}", data=json.dumps(edata_dict))

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("kv_pair", [kv_data_dict_only_key, kv_data_dict_only_value])
    def test_save__kv_pair_has_only_one_element__successful(self, client, kv_pair):
        field = {"fieldCode": uuid.uuid4().hex, "data": kv_pair}
        edata_dict = {
            "fields": [field],
            "groups": random.choice((None, [{"order": 1, "name": "kv_name", "elements": [field["data"]["id"]]}])),
        }

        response = client.put(f"{self.endpoint}/{random.randint(1, 10000)}", data=json.dumps(edata_dict))
        assert response.status_code == HTTPStatus.OK

    def test_save__edata_with_several_groups__successful(self, client, extracted_data_dict_with_all_fields_and_groups):
        doc_id = random.randint(1, 10000)
        response = client.put(
            f"{self.endpoint}/{doc_id}", data=json.dumps(extracted_data_dict_with_all_fields_and_groups)
        )
        assert response.status_code == HTTPStatus.OK

        response = client.get(f"{self.endpoint}/{doc_id}")

        assert response.status_code == HTTPStatus.OK
        assert extracted_data_dict_with_all_fields_and_groups["groups"] == response.json()["groups"]

    def test_put_table_chunked_data__edata_not_exists__created(self, client, chunked_data):
        response = client.put(
            f"{self.endpoint}/{random.randint(1, 10)}/fields/{uuid4().hex}/table/chunk",
            json=chunked_data,
        )

        assert response.status_code == HTTPStatus.OK

    def test_put_table_chunked_data__edata_exists__updated(self, client, chunked_data):
        document_id = random.randint(1, 10)
        field_code = uuid4().hex
        client.put(
            f"{self.endpoint}/{document_id}/fields/{field_code}/table/chunk",
            json=chunked_data,
        )
        response = client.put(
            f"{self.endpoint}/{document_id}/fields/{field_code}/table/chunk",
            json=chunked_data,
        )

        assert response.status_code == HTTPStatus.OK

    def test_put_table_info__info_exists__updated(self, client, table_info):
        document_id = random.randint(1, 10)
        field_code = uuid4().hex
        client.put(
            f"{self.endpoint}/{document_id}/fields/{field_code}/table/info",
            json=table_info,
        )
        response = client.put(
            f"{self.endpoint}/{document_id}/fields/{field_code}/table/info",
            json=table_info,
        )

        assert response.status_code == HTTPStatus.OK

    def test_put_chunked_data_and_info__not_exist__created(
        self, client, table_info_and_data, extracted_data_dict_with_several_fields_v2
    ):
        document_id = random.randint(1, 10)
        field_code = uuid4().hex
        client.put(
            f"{self.endpoint}/{document_id}",
            json=extracted_data_dict_with_several_fields_v2,
        )
        client.put(
            f"{self.endpoint}/{document_id}/fields/{field_code}/table/info",
            json=table_info_and_data["table_info"],
        )
        client.put(
            f"{self.endpoint}/{document_id}/fields/{field_code}/table/chunk",
            json=table_info_and_data["chunked_data"],
        )

        response = client.get(f"{self.endpoint}/{document_id}")
        gotten_data = response.json()
        expected_field = next(filter(lambda data: data["fieldCode"] == field_code, gotten_data["fields"]))

        assert gotten_data["documentId"] == document_id
        assert expected_field == self._gather_fields_from(table_info_and_data, field_code)

    def _gather_fields_from(self, table_info_and_data: CommonDictType, field_code: str) -> CommonDictType:
        table_info = table_info_and_data["table_info"]["info"]
        cells = table_info_and_data["chunked_data"]["cells"]
        list_index = table_info_and_data["table_info"]["listIndex"]
        aliases = ({table_info["id"]: table_info["alias"]} if table_info.get("alias") else None) or (
            {} if list_index is not None else None
        )

        full_field_data = {
            "columns": table_info["columns"],
            "id": table_info["id"],
            "rows": table_info["rows"],
            "sourceBboxCoordinates": table_info.get("sourceBboxCoordinates"),
            "sourceTableCoordinates": table_info.get("sourceTableCoordinates"),
            "meta": None,
            "paginatedRows": None,
            "cells": [self._gather_cell_from(cell) for cell in cells],
        }

        return {
            "data": [full_field_data] if list_index else full_field_data,
            "fieldCode": field_code,
            "aliases": aliases,
        }

    @staticmethod
    def _gather_cell_from(cell: CommonDictType) -> CommonDictType:
        return {
            "confidence": cell["confidence"] if cell.get("confidence") else -1.0,
            "pk": cell["pk"],
            "value": cell["value"],
            "coordinates": TestExtractedDataAPI._gather_cell_table_coordinates(cell["coordinates"]),
            "sourceBboxCoordinates": cell.get("sourceBboxCoordinates"),
            "sourceTableCoordinates": cell.get("sourceTableCoordinates"),
            "sourceTextCoordinates": cell.get("sourceTextCoordinates"),
        }

    @staticmethod
    def _gather_cell_table_coordinates(coordinates: CommonDictType) -> CommonDictType:
        return {
            "column": coordinates["column"],
            "row": coordinates["row"],
            "rowspan": coordinates["row_span"],
            "colspan": coordinates["column_span"],
        }

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
        edata = {
            "fields": [
                {"fieldCode": list_chunk_table["fieldPk"], "data": list_chunk_table["data"]},
                {"fieldCode": "1", "data": string_data_dict_bbox_coordinates},
                {
                    "fieldCode": corleone_table_dict_chunk_json[0]["fieldPk"],
                    "data": corleone_table_dict_chunk_json[0]["data"],
                },
            ]
        }

        put_response = client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata))
        response = client.get(f"{self.endpoint}/{doc_id}", params=params)

        res_json = response.json()["fields"]
        assert response.status_code == HTTPStatus.OK
        assert len(res_json) == 3
        assert res_json[1]["data"]["cells"] == []
        assert res_json[2]["data"][0]["cells"] == []
        assert res_json[2]["data"][1]["cells"] == []

    def test_get_paginated_extract_data__only_non_paginated_field__successful(self, client):
        doc_id = random.randint(1, 10000)
        edata = {"fields": [{"fieldCode": uuid.uuid4().hex, "data": string_data_dict_bbox_coordinates}]}
        client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata))

        response = client.get(f"{self.endpoint}/{doc_id}", params={"rowsPerChunk": 2})
        res_json = response.json()["fields"]
        assert response.status_code == HTTPStatus.OK
        assert len(res_json) == 1

    def test_get_paginated_extract_data__only_paginated_field__successful(self, client):
        doc_id = random.randint(1, 10000)
        edata = {
            "fields": [
                {"fieldCode": list_chunk_table["fieldPk"], "data": list_chunk_table["data"]},
                {
                    "fieldCode": corleone_table_dict_chunk_json[0]["fieldPk"],
                    "data": corleone_table_dict_chunk_json[0]["data"],
                },
            ]
        }
        client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata))

        response = client.get(f"{self.endpoint}/{doc_id}", params={"rowsPerChunk": 2})
        res_json = response.json()["fields"]

        assert response.status_code == HTTPStatus.OK
        assert len(res_json) == 2
        assert res_json[0]["data"]["cells"] == []
        assert res_json[1]["data"][0]["cells"] == []
        assert res_json[1]["data"][1]["cells"] == []

    def test_patch_table_extracted_data__valid_list_data__successful(
        self, client, list_chunk_table_without_ids_in_cells
    ):
        doc_id = random.randint(1, 10000)
        field_code = list_chunk_table_without_ids_in_cells["fieldPk"]
        data = list_chunk_table_without_ids_in_cells["data"]
        edata = {
            "fields": [
                {
                    "fieldCode": field_code,
                    "data": data,
                },
            ]
        }
        saved_edata = client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata)).json()["fields"][0]["data"]

        cell_1_index, cell_2_index = random.sample(range(len(saved_edata[0]["cells"])), 2)
        updated_value = saved_edata[0]["cells"][cell_1_index]["value"] = saved_edata[0]["cells"][cell_2_index][
            "value"
        ] = "I was updated"
        updated_confidence = saved_edata[1]["cells"][cell_1_index]["confidence"] = saved_edata[1]["cells"][
            cell_2_index
        ]["confidence"] = 0.111111111111111111111111

        response_1 = client.patch(
            f"{self.endpoint}/{doc_id}/fields/{field_code}",
            data=json.dumps({"cells": [*saved_edata[0]["cells"], *saved_edata[1]["cells"]]}),
        )
        assert response_1.status_code == HTTPStatus.OK

        response_2 = client.get(f"{self.endpoint}/{doc_id}")
        assert response_2.status_code == HTTPStatus.OK

        updated_cells_table_1 = response_2.json()["fields"][0]["data"][0]["cells"]
        updated_cells_table_2 = response_2.json()["fields"][0]["data"][1]["cells"]
        assert updated_cells_table_1[cell_1_index]["value"] == updated_value
        assert updated_cells_table_1[cell_2_index]["value"] == updated_value
        assert updated_cells_table_2[cell_1_index]["value"] != updated_value
        assert updated_cells_table_2[cell_2_index]["value"] != updated_value
        assert updated_cells_table_2[cell_1_index]["confidence"] == updated_confidence
        assert updated_cells_table_2[cell_2_index]["confidence"] == updated_confidence
        assert updated_cells_table_1[cell_1_index]["confidence"] != updated_confidence
        assert updated_cells_table_1[cell_2_index]["confidence"] != updated_confidence

    def test_patch_table_extracted_data__valid_data__successful(self, client):
        doc_id = random.randint(1, 10000)
        field_code = corleone_table_dict_chunk_json[0]["fieldPk"]
        data = corleone_table_dict_chunk_json[0]["data"]
        edata = {
            "fields": [
                {
                    "fieldCode": field_code,
                    "data": data,
                },
            ]
        }
        client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata))

        cell_1_index, cell_2_index = random.sample(range(len(data["cells"])), 2)
        updated_value = data["cells"][cell_1_index]["value"] = data["cells"][cell_2_index]["value"] = "I was updated"
        updated_confidence = data["cells"][cell_1_index]["confidence"] = data["cells"][cell_2_index][
            "confidence"
        ] = random.random()

        response_1 = client.patch(
            f"{self.endpoint}/{doc_id}/fields/{field_code}", data=json.dumps({"cells": data["cells"]})
        )
        assert response_1.status_code == HTTPStatus.OK

        response_2 = client.get(f"{self.endpoint}/{doc_id}")
        assert response_2.status_code == HTTPStatus.OK

        updated_cells = response_2.json()["fields"][0]["data"]["cells"]
        for ind, el in enumerate(data["cells"]):
            if ind not in (cell_1_index, cell_2_index):
                assert all(
                    (el["value"] == updated_cells[ind]["value"], el["confidence"] == updated_cells[ind]["confidence"])
                )
        assert updated_cells[cell_1_index]["value"] == updated_cells[cell_2_index]["value"] == updated_value
        assert (
            updated_cells[cell_1_index]["confidence"] == updated_cells[cell_2_index]["confidence"] == updated_confidence
        )

    def test_patch_table_extracted_data__empty_data__no_errors(self, client):
        doc_id = random.randint(1, 10000)
        field_code = corleone_table_dict_chunk_json[0]["fieldPk"]
        data = corleone_table_dict_chunk_json[0]["data"]
        edata = {
            "fields": [
                {
                    "fieldCode": field_code,
                    "data": data,
                },
            ]
        }
        client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata))

        response = client.patch(f"{self.endpoint}/{doc_id}/fields/{field_code}", data=json.dumps({"cells": []}))
        assert response.status_code == HTTPStatus.OK

    def test_patch_table_extracted_data__user_hasnt_access__forbidden(self, client, other_organisation_user):
        doc_id = random.randint(1, 10000)
        field_code = corleone_table_dict_chunk_json[0]["fieldPk"]
        data = corleone_table_dict_chunk_json[0]["data"]
        edata = {
            "fields": [
                {
                    "fieldCode": field_code,
                    "data": data,
                },
            ]
        }
        client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(edata))

        user.set(other_organisation_user)

        response = client.patch(
            f"{self.endpoint}/{doc_id}/fields/{field_code}", data=json.dumps({"cells": data["cells"]})
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_save_edata__invalid_table_cell_coordinates__error(
        self, client, extracted_data_table_field_with_invalid_cell_table_coordinates_v2
    ):
        response = client.put(
            f"{self.endpoint}/{random.randint(1, 10000)}",
            data=json.dumps(extracted_data_table_field_with_invalid_cell_table_coordinates_v2),
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.aliases
    def test_get_edata__aliases_presetns(
        self, client, empty_extracted_data, extracted_string_list_factory, extracted_data_repository
    ):
        empty_extracted_data.add_string_list(extracted_string_list_factory(with_aliases=True))
        extracted_data_repository.save(empty_extracted_data)
        response = client.get(f"{self.endpoint}/{empty_extracted_data.document_id}")

        assert response.status_code == HTTPStatus.OK
        assert "aliases" in response.json()["fields"][0]

    @pytest.mark.aliases
    def test_get_edata__field_doesnt_support_aliases__alisases_doesnt_present(
        self, client, empty_extracted_data, extracted_string_factory_with_bbox_coord, extracted_data_repository
    ):
        empty_extracted_data.add_string_list(extracted_string_factory_with_bbox_coord())
        extracted_data_repository.save(empty_extracted_data)
        response = client.get(f"{self.endpoint}/{empty_extracted_data.document_id}")

        assert response.status_code == HTTPStatus.OK
        assert "aliases" not in response.json()["fields"][0] or response.json()["fields"][0]["aliases"] is None

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
        for field in response.json()["fields"]:
            if isinstance(field["data"], list):
                assert "aliases" in field and field["aliases"] is not None
            else:
                assert "aliases" not in field or field["aliases"] is None

    @pytest.mark.aliases
    def test_save_edata__valid_edata_with_aliases__successful(
        self, client, extracted_data_dict_with_several_fields_and_aliases_v2
    ):
        response = client.put(
            f"{self.endpoint}/{random.randint(1, 10000)}",
            data=json.dumps(extracted_data_dict_with_several_fields_and_aliases_v2),
        )

        assert response.status_code == HTTPStatus.OK
        for field in response.json()["fields"]:
            if isinstance(field["data"], list):
                assert len(field["aliases"]) == len(field["data"])
            else:
                assert "aliases" not in field or field["aliases"] is None

    @pytest.mark.aliases
    @pytest.mark.parametrize(
        "aliases", [{list_string_data_dict[0]["id"]: ""}, {list_string_data_dict[0]["id"]: "a" * 300}]
    )
    def test_save_edata__invalid_aliases_422_error(self, aliases, client):
        edata = [{"fieldCode": uuid.uuid4().hex, "data": list_string_data_dict, "aliases": aliases}]
        response = client.put(
            f"{self.endpoint}/{random.randint(1, 10000)}",
            data=json.dumps({"fields": edata, "groups": []}),
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.aliases
    def test_get_edata__with_aliases__ok(self, client, saved_extacted_data_with_with_aliases):
        response = client.get(f"{self.endpoint}/{saved_extacted_data_with_with_aliases.document_id}")

        assert response.status_code == HTTPStatus.OK
        for field in response.json()["fields"]:
            assert "aliases" in field

    def test_update_aliases__valid_data__ok(self, client, saved_extacted_data_with_with_aliases):
        field_for_update = random.choice(saved_extacted_data_with_with_aliases.fields)
        updated_alias = "Hello World"
        data = {"updatedAliases": {field_for_update.data.elements[0].id(): updated_alias}}

        response = client.patch(
            f"{self.endpoint}/{saved_extacted_data_with_with_aliases.document_id}/fields/{field_for_update.field_code}/aliases",
            json=data,
        )

        assert response.status_code == HTTPStatus.OK

        updated_edata = client.get(f"{self.endpoint}/{saved_extacted_data_with_with_aliases.document_id}").json()[
            "fields"
        ]
        updated_field = next(filter(lambda field: field["fieldCode"] == field_for_update.field_code, updated_edata))

        assert updated_field["aliases"][field_for_update.data.elements[0].id()] == updated_alias

    def test_update_aliases__valid_data__updated_only_needed(self, client, saved_extacted_data_with_with_aliases):
        field_for_update = random.choice(saved_extacted_data_with_with_aliases.fields)
        updated_alias = "Hello World"
        data = {"updatedAliases": {field_for_update.data.elements[0].id(): updated_alias}}

        client.patch(
            f"{self.endpoint}/{saved_extacted_data_with_with_aliases.document_id}/fields/{field_for_update.field_code}/aliases",
            json=data,
        )

        field_for_update.data.aliases[field_for_update.data.elements[0].id] = updated_alias
        updated_edata = client.get(f"{self.endpoint}/{saved_extacted_data_with_with_aliases.document_id}").json()[
            "fields"
        ]

        for field in updated_edata:
            orig_field = next(
                filter(lambda el: el.field_code == field["fieldCode"], saved_extacted_data_with_with_aliases.fields)
            )

            assert field["aliases"] == {element_id(): alias for element_id, alias in orig_field.data.aliases.items()}

    @pytest.mark.parametrize("alias", ["", "HST_" * 70])
    def test_update_aliases__invalid_data__error(self, alias, client, saved_extacted_data_with_with_aliases):
        field_for_update = random.choice(saved_extacted_data_with_with_aliases.fields)
        data = {"updatedAliases": {field_for_update.data.elements[0].id(): alias}}

        response = client.patch(
            f"{self.endpoint}/{saved_extacted_data_with_with_aliases.document_id}/fields/{field_for_update.field_code}/aliases",
            json=data,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_get_fields__edata_doesnt_exist__return_404(self, client):
        response = client.get(
            f"{self.endpoint}/1/fields",
            params={"fieldCodes": ["code1"]},
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_fields__no_field_codes__return_422(self, client, saved_extracted_data):
        response = client.get(
            f"{self.endpoint}/{saved_extracted_data.document_id}/fields",
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_fields__fields_exist__return_matching_fields(self, client, saved_extracted_data):
        target_codes = [saved_extracted_data.fields[0].field_code, saved_extracted_data.fields[1].field_code]

        response = client.get(
            f"{self.endpoint}/{saved_extracted_data.document_id}/fields",
            params={"fieldCodes": target_codes},
        )

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert len(body) == 2
        returned_codes = {f["fieldCode"] for f in body}
        assert returned_codes == set(target_codes)

    def test_get_fields__some_codes_not_found__return_404(self, client, saved_extracted_data):
        response = client.get(
            f"{self.endpoint}/{saved_extracted_data.document_id}/fields",
            params={"fieldCodes": [saved_extracted_data.fields[0].field_code, "nonexistent_code"]},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_aliases__invalid_element_id__error(self, client, saved_extacted_data_with_with_aliases):
        field_for_update = random.choice(saved_extacted_data_with_with_aliases.fields)
        data = {"updatedAliases": {"fake_element_id": "Hello World"}}

        response = client.patch(
            f"{self.endpoint}/{saved_extacted_data_with_with_aliases.document_id}/fields/{field_for_update.field_code}/aliases",
            json=data,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_update_aliases__one_of_element_id_invalid__error(self, client, saved_extacted_data_with_with_aliases):
        field_for_update = random.choice(saved_extacted_data_with_with_aliases.fields)
        data = {
            "updatedAliases": {
                field_for_update.data.elements[0].id(): "Hello World",
                "fake_element_id": "Hello World Again",
            }
        }

        response = client.patch(
            f"{self.endpoint}/{saved_extacted_data_with_with_aliases.document_id}/fields/{field_for_update.field_code}/aliases",
            json=data,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
