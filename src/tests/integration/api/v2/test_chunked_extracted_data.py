import json
import random
from http import HTTPStatus

import pytest

from deps_extraction.constants import BASE_API_PREFIX, V2_PREFIX
from deps_extraction.infrastructure.data_object_accessors import user
from tests.data.chunked_data import (
    chunk_1_x_1_response,
    chunk_1_x_2_response,
    chunk_1_x_3_response,
    chunk_1_x_4_response,
    chunk_1_x_5_response,
    chunk_1_x_6_response,
    chunk_2_x_1_response,
    chunk_2_x_2_response,
    chunk_2_x_3_response,
    chunk_3_x_1_response,
    chunk_3_x_2_response,
    chunk_4_x_1_response,
    chunk_4_x_2_response,
    chunk_5_x_1_response,
    chunk_5_x_2_response,
    chunk_15_x_1_response,
    corleone_table_dict_chunk,
    list_chunk_table,
)


@pytest.fixture(
    params=(
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_1_x_1_response,
            2,
            {"rowsPerChunk": 1, "rowsChunk": 1},
            {"rowsPerChunk": 1, "rowsChunk": 1, "listIndex": 0},
            {"rowsPerChunk": 1, "rowsChunk": 1, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_1_x_2_response,
            2,
            {"rowsPerChunk": 1, "rowsChunk": 2},
            {"rowsPerChunk": 1, "rowsChunk": 2, "listIndex": 0},
            {"rowsPerChunk": 1, "rowsChunk": 2, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_1_x_3_response,
            3,
            {"rowsPerChunk": 1, "rowsChunk": 3},
            {"rowsPerChunk": 1, "rowsChunk": 3, "listIndex": 0},
            {"rowsPerChunk": 1, "rowsChunk": 3, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_1_x_4_response,
            2,
            {"rowsPerChunk": 1, "rowsChunk": 4},
            {"rowsPerChunk": 1, "rowsChunk": 4, "listIndex": 0},
            {"rowsPerChunk": 1, "rowsChunk": 4, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_1_x_5_response,
            3,
            {"rowsPerChunk": 1, "rowsChunk": 5},
            {"rowsPerChunk": 1, "rowsChunk": 5, "listIndex": 0},
            {"rowsPerChunk": 1, "rowsChunk": 5, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_1_x_6_response,
            3,
            {"rowsPerChunk": 1, "rowsChunk": 6},
            {"rowsPerChunk": 1, "rowsChunk": 6, "listIndex": 0},
            {"rowsPerChunk": 1, "rowsChunk": 6, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_2_x_1_response,
            3,
            {"rowsPerChunk": 2, "rowsChunk": 1},
            {"rowsPerChunk": 2, "rowsChunk": 1, "listIndex": 0},
            {"rowsPerChunk": 2, "rowsChunk": 1, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_2_x_2_response,
            4,
            {"rowsPerChunk": 2, "rowsChunk": 2},
            {"rowsPerChunk": 2, "rowsChunk": 2, "listIndex": 0},
            {"rowsPerChunk": 2, "rowsChunk": 2, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_2_x_3_response,
            5,
            {"rowsPerChunk": 2, "rowsChunk": 3},
            {"rowsPerChunk": 2, "rowsChunk": 3, "listIndex": 0},
            {"rowsPerChunk": 2, "rowsChunk": 3, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_3_x_1_response,
            6,
            {"rowsPerChunk": 3, "rowsChunk": 1},
            {"rowsPerChunk": 3, "rowsChunk": 1, "listIndex": 0},
            {"rowsPerChunk": 3, "rowsChunk": 1, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_3_x_2_response,
            7,
            {"rowsPerChunk": 3, "rowsChunk": 2},
            {"rowsPerChunk": 3, "rowsChunk": 2, "listIndex": 0},
            {"rowsPerChunk": 3, "rowsChunk": 2, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_4_x_1_response,
            7,
            {"rowsPerChunk": 4, "rowsChunk": 1},
            {"rowsPerChunk": 4, "rowsChunk": 1, "listIndex": 0},
            {"rowsPerChunk": 4, "rowsChunk": 1, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_4_x_2_response,
            5,
            {"rowsPerChunk": 4, "rowsChunk": 2},
            {"rowsPerChunk": 4, "rowsChunk": 2, "listIndex": 0},
            {"rowsPerChunk": 4, "rowsChunk": 2, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_5_x_1_response,
            10,
            {"rowsPerChunk": 5, "rowsChunk": 1},
            {"rowsPerChunk": 5, "rowsChunk": 1, "listIndex": 0},
            {"rowsPerChunk": 5, "rowsChunk": 1, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_5_x_2_response,
            3,
            {"rowsPerChunk": 5, "rowsChunk": 2},
            {"rowsPerChunk": 5, "rowsChunk": 2, "listIndex": 0},
            {"rowsPerChunk": 5, "rowsChunk": 2, "listIndex": 1},
        ),
        (
            corleone_table_dict_chunk,
            list_chunk_table,
            chunk_15_x_1_response,
            12,
            {"rowsPerChunk": 15, "rowsChunk": 1},
            {"rowsPerChunk": 15, "rowsChunk": 1, "listIndex": 0},
            {"rowsPerChunk": 15, "rowsChunk": 1, "listIndex": 1},
        ),
    )
)
def extracted_data_params(request):
    data, list_data, expected_response, len_cells, params, list_parmas, list_params_1 = request.param
    json_data = json.loads(data)
    json_data.append(list_data)
    return json_data, expected_response, len_cells, params, list_parmas, list_params_1


class TestChunkedExtractedData:
    endpoint = f"{BASE_API_PREFIX}/v1/extracted-data"

    def test_get_chunked_extract_data_merged_rows(self, client, extracted_data_params):
        doc_id = random.randint(1, 10000)
        all_data, expected_response, len_cells, params, list_parmas, list_params_1 = extracted_data_params
        client.put(f"{self.endpoint}/{doc_id}", data=json.dumps(all_data))

        response = client.get(f"{BASE_API_PREFIX}{V2_PREFIX}/extracted-data/{doc_id}/fields/76/chunk", params=params)
        list_response = client.get(
            f"{BASE_API_PREFIX}{V2_PREFIX}/extracted-data/{doc_id}/fields/77/chunk", params=list_parmas
        )
        list_response_1 = client.get(
            f"{BASE_API_PREFIX}{V2_PREFIX}/extracted-data/{doc_id}/fields/77/chunk", params=list_params_1
        )

        assert all(list(filter(lambda x: x.status_code == HTTPStatus.OK, [response, list_response, list_response_1])))
        assert (
            response.json()["data"]
            == list_response.json()["data"]
            == list_response_1.json()["data"]
            == expected_response["data"]
        )
        assert all(
            list(
                filter(
                    lambda x: len(x.json()["data"]["cells"]) == len_cells, [response, list_response, list_response_1]
                )
            )
        )

    def test_get_chuncked_extracted_data__no_edata__403(self, client):
        response = client.get(
            f"{BASE_API_PREFIX}{V2_PREFIX}/extracted-data/111/fields/76/chunk",
            params={"rowsPerChunk": 15, "rowsChunk": 1},
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_chuncked_extracted_data__no_access__forbidden(self, client, other_organisation_user):
        doc_id = random.randint(1, 10000)
        client.put(f"{self.endpoint}/{doc_id}", data=corleone_table_dict_chunk)

        user.set(other_organisation_user)

        response = client.get(
            f"{BASE_API_PREFIX}{V2_PREFIX}/extracted-data/{doc_id}/fields/76/chunk",
            params={"rowsPerChunk": 15, "rowsChunk": 1},
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
