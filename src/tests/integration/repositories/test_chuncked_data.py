import copy
import json
import random

import pytest
from deps_extracted_data.model.extracted_data import (
    ExtractedDataFactory,
    ExtractedFieldFactory,
)
from deps_extracted_data.model.extracted_data.extracted_fields import (
    GenericList,
    TableList,
)

from deps_extraction.domain.dtos import ExtractedDataPaginationParamsObject
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
    list_chunk_table_raw,
)


@pytest.mark.parametrize(
    "extracted_data_params",
    [
        (chunk_1_x_1_response, {"rows_per_chunk": 1, "rows_chunk": 1}),
        (chunk_1_x_2_response, {"rows_per_chunk": 1, "rows_chunk": 2}),
        (chunk_1_x_3_response, {"rows_per_chunk": 1, "rows_chunk": 3}),
        (chunk_1_x_4_response, {"rows_per_chunk": 1, "rows_chunk": 4}),
        (chunk_1_x_5_response, {"rows_per_chunk": 1, "rows_chunk": 5}),
        (chunk_1_x_6_response, {"rows_per_chunk": 1, "rows_chunk": 6}),
        (chunk_2_x_1_response, {"rows_per_chunk": 2, "rows_chunk": 1}),
        (chunk_2_x_2_response, {"rows_per_chunk": 2, "rows_chunk": 2}),
        (chunk_2_x_3_response, {"rows_per_chunk": 2, "rows_chunk": 3}),
        (chunk_3_x_1_response, {"rows_per_chunk": 3, "rows_chunk": 1}),
        (chunk_3_x_2_response, {"rows_per_chunk": 3, "rows_chunk": 2}),
        (chunk_4_x_1_response, {"rows_per_chunk": 4, "rows_chunk": 1}),
        (chunk_4_x_2_response, {"rows_per_chunk": 4, "rows_chunk": 2}),
        (chunk_5_x_1_response, {"rows_per_chunk": 5, "rows_chunk": 1}),
        (chunk_5_x_2_response, {"rows_per_chunk": 5, "rows_chunk": 2}),
        (chunk_15_x_1_response, {"rows_per_chunk": 15, "rows_chunk": 1}),
    ],
)
def test_get_field_chunk__table_field__valid_chunk_return(
    extracted_data_repository, extracted_table_factory_from_dict, extracted_data_params, chuncked_repository
):
    expected_chunk, chunk_params = extracted_data_params
    doc_id = random.randint(1, 10000)
    field_code = "damn_chunk"
    dict_edata = json.loads(corleone_table_dict_chunk)
    field = extracted_table_factory_from_dict(
        cells=dict_edata[0]["data"]["cells"],
        field_code=field_code,
        columns=[col["x"] for col in dict_edata[0]["data"]["columns"]],
        rows=[row["y"] for row in dict_edata[0]["data"]["rows"]],
        source_table_coordinates=dict_edata[0]["data"]["sourceTableCoordinates"],
    )
    edata = ExtractedDataFactory().make_extracted_data(doc_id)
    edata.add_table(field)
    extracted_data_repository.save(edata)
    pagination_params = ExtractedDataPaginationParamsObject(**chunk_params)

    result = chuncked_repository.get_field_chunk(doc_id, field_code, pagination_params)

    assert expected_chunk["meta"] == result.meta.model_dump()
    assert expected_chunk["data"] == result.data.dict(by_alias=True)


@pytest.mark.parametrize(
    "extracted_data_params",
    [
        (chunk_1_x_1_response, {"rows_per_chunk": 1, "rows_chunk": 1, "list_index": 0}),
        (chunk_1_x_2_response, {"rows_per_chunk": 1, "rows_chunk": 2, "list_index": 0}),
        (chunk_1_x_3_response, {"rows_per_chunk": 1, "rows_chunk": 3, "list_index": 1}),
        (chunk_1_x_4_response, {"rows_per_chunk": 1, "rows_chunk": 4, "list_index": 1}),
        (chunk_1_x_5_response, {"rows_per_chunk": 1, "rows_chunk": 5, "list_index": 0}),
        (chunk_1_x_6_response, {"rows_per_chunk": 1, "rows_chunk": 6, "list_index": 0}),
        (chunk_2_x_1_response, {"rows_per_chunk": 2, "rows_chunk": 1, "list_index": 1}),
        (chunk_2_x_2_response, {"rows_per_chunk": 2, "rows_chunk": 2, "list_index": 1}),
        (chunk_2_x_3_response, {"rows_per_chunk": 2, "rows_chunk": 3, "list_index": 0}),
        (chunk_3_x_1_response, {"rows_per_chunk": 3, "rows_chunk": 1, "list_index": 0}),
        (chunk_3_x_2_response, {"rows_per_chunk": 3, "rows_chunk": 2, "list_index": 1}),
        (chunk_4_x_1_response, {"rows_per_chunk": 4, "rows_chunk": 1, "list_index": 1}),
        (chunk_4_x_2_response, {"rows_per_chunk": 4, "rows_chunk": 2, "list_index": 0}),
        (chunk_5_x_1_response, {"rows_per_chunk": 5, "rows_chunk": 1, "list_index": 0}),
        (chunk_5_x_2_response, {"rows_per_chunk": 5, "rows_chunk": 2, "list_index": 1}),
        (chunk_15_x_1_response, {"rows_per_chunk": 15, "rows_chunk": 1, "list_index": 1}),
    ],
)
def test_get_field_chunk__table_list_field__valid_chunk_return(
    extracted_data_repository,
    extracted_table_factory_from_dict,
    extracted_data_params,
    chuncked_repository,
):
    expected_chunk, chunk_params = extracted_data_params
    expected_chunk["meta"]["list_index"] = chunk_params["list_index"]
    doc_id = random.randint(1, 10000)
    field_code = "damn_chunk_list"
    dict_edata = json.loads(list_chunk_table_raw)
    table_1 = extracted_table_factory_from_dict(
        cells=dict_edata["data"][0]["cells"],
        field_code=field_code,
        columns=[col["x"] for col in dict_edata["data"][0]["columns"]],
        rows=[row["y"] for row in dict_edata["data"][0]["rows"]],
        source_table_coordinates=dict_edata["data"][0]["sourceTableCoordinates"],
    )
    table_2 = extracted_table_factory_from_dict(
        cells=dict_edata["data"][1]["cells"],
        field_code=field_code,
        columns=[col["x"] for col in dict_edata["data"][1]["columns"]],
        rows=[row["y"] for row in dict_edata["data"][1]["rows"]],
        source_table_coordinates=dict_edata["data"][1]["sourceTableCoordinates"],
    )
    edata = ExtractedDataFactory().make_extracted_data(doc_id)
    field = ExtractedFieldFactory().create_table_list(field_code, [table_1.data, table_2.data])
    edata.add_table_list(field)
    extracted_data_repository.save(edata)
    pagination_params = ExtractedDataPaginationParamsObject(**chunk_params)

    result = chuncked_repository.get_field_chunk(doc_id, field_code, pagination_params)

    assert expected_chunk["meta"] == result.meta.model_dump()
    assert expected_chunk["data"] == result.data.model_dump(by_alias=True)


def test_get_field_chunk__table_field_with_text_coordinates_for_cell__ok(
    extracted_data_repository,
    extracted_table_factory_with_text_cell_coord,
    chuncked_repository,
):
    doc_id = random.randint(1, 10000)
    field = extracted_table_factory_with_text_cell_coord()
    edata = ExtractedDataFactory().make_extracted_data(doc_id)
    edata.add_table(field)
    extracted_data_repository.save(edata)

    result = chuncked_repository.get_field_chunk(
        doc_id,
        field.field_code,
        ExtractedDataPaginationParamsObject(rows_chunk=1, rows_per_chunk=1),
    )

    assert result


def test_get_field_chunk__table_field_with_bbox_coordinates_for_cell__ok(
    extracted_data_repository,
    extracted_table_factory_with_bbox_coord,
    chuncked_repository,
):
    doc_id = random.randint(1, 10000)
    field = extracted_table_factory_with_bbox_coord()
    edata = ExtractedDataFactory().make_extracted_data(doc_id)
    edata.add_table(field)
    extracted_data_repository.save(edata)

    result = chuncked_repository.get_field_chunk(
        doc_id,
        field.field_code,
        ExtractedDataPaginationParamsObject(rows_chunk=1, rows_per_chunk=1),
    )

    assert result


def test_batch_partial_update_field__ok(
    extracted_data_repository,
    extracted_table_factory_with_bbox_coord,
    chuncked_repository,
):
    doc_id = random.randint(1, 10000)
    field = extracted_table_factory_with_bbox_coord()
    edata = ExtractedDataFactory().make_extracted_data(doc_id)
    edata.add_table(field)
    extracted_data_repository.save(edata)
    chuncked_repository.batch_partial_update_field(
        doc_id,
        field.field_code,
        [
            {
                "value": "updated_value",
                "confidence": 0.123456,
                "_id": field.data.cells[1].id(),
                "source_bbox_coordinates": [],
            }
        ],
    )

    updated_edata = extracted_data_repository.find(doc_id)

    assert updated_edata.table_fields[0].data.cells[1].value == "updated_value"
    assert updated_edata.table_fields[0].data.cells[1].confidence == 0.123456
    assert updated_edata.table_fields[0].data.cells[0].value != "updated_value"
    assert updated_edata.table_fields[0].data.cells[0].confidence != 0.123456


def test_batch_partial_update_list_table_field__ok(
    extracted_data_repository,
    extracted_table_factory_with_bbox_coord,
    chuncked_repository,
):
    doc_id = random.randint(1, 10000)
    table_1 = extracted_table_factory_with_bbox_coord()
    table_2 = extracted_table_factory_with_bbox_coord()
    edata = ExtractedDataFactory().make_extracted_data(doc_id)
    edata.add_table_list(TableList(table_1.field_code, GenericList(elements=[table_1.data, table_2.data])))
    extracted_data_repository.save(edata)

    chuncked_repository.batch_partial_update_field(
        doc_id,
        table_1.field_code,
        [
            {
                "value": "updated_value",
                "confidence": 0.123456,
                "_id": table_1.data.cells[1].id(),
                "source_bbox_coordinates": [],
            }
        ],
    )

    updated_edata = extracted_data_repository.find(doc_id)

    assert updated_edata.table_list_fields[0].data.elements[0].cells[1].value == "updated_value"
    assert updated_edata.table_list_fields[0].data.elements[1].cells[1].value != "updated_value"
    assert updated_edata.table_list_fields[0].data.elements[0].cells[1].confidence == 0.123456
    assert updated_edata.table_list_fields[0].data.elements[1].cells[1].confidence != 0.123456
