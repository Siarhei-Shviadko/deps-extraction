from uuid import uuid4

from deps_extracted_data.serializers.v1 import (
    SerializedExtractedData,
    SerializedExtractedField,
)

from deps_extraction.api.helpers.extracted_data import build_extracted_data
from tests.data.extracted_data import (
    kv_data_dict_bbox_coordinates,
    list_kv_data_dict,
    list_string_data_dict,
    list_table_data_dict,
    string_data_dict_bbox_coordinates,
    table_data_dict_bbox_coordinates,
)


def test_build_table_extracted_data__successful():
    field = SerializedExtractedField(**{"fieldPk": uuid4().hex, "data": table_data_dict_bbox_coordinates})
    edata = build_extracted_data([field])

    assert edata["groups"][0].order == field.data.set_index
    assert edata["groups"][0].elements[0] == field.data.id


def test_build_list_table_extracted_data__successful():
    field = SerializedExtractedField(**{"fieldPk": uuid4().hex, "data": list_table_data_dict})
    edata = build_extracted_data([field])

    assert len(edata["groups"]) == len(field.data)
    for i in range(len(edata["groups"])):
        assert edata["groups"][i].order == field.data[i].set_index
        assert edata["groups"][i].elements[0] == field.data[i].id


def test_build_string_extracted_data__successful():
    field = SerializedExtractedField(**{"fieldPk": uuid4().hex, "data": string_data_dict_bbox_coordinates})
    edata = build_extracted_data([field])

    assert edata["groups"][0].order == field.data.set_index
    assert edata["groups"][0].elements[0] == field.data.id


def test_build_list_string_extracted_data__successful():
    field = SerializedExtractedField(**{"fieldPk": uuid4().hex, "data": list_string_data_dict})
    edata = build_extracted_data([field])

    assert len(edata["groups"]) == len(field.data)
    for i in range(len(edata["groups"])):
        assert edata["groups"][i].order == field.data[i].set_index
        assert edata["groups"][i].elements[0] == field.data[i].id


def test_build_kv_pair_extracted_data__successful():
    field = SerializedExtractedField(**{"fieldPk": uuid4().hex, "data": kv_data_dict_bbox_coordinates})
    edata = build_extracted_data([field])

    assert edata["groups"][0].order == field.data.key.set_index
    assert edata["groups"][0].order == field.data.value.set_index
    assert edata["groups"][0].elements[0] == field.data.id


def test_build_list_kv_pair_extracted_data__successful():
    field = SerializedExtractedField(**{"fieldPk": uuid4().hex, "data": list_kv_data_dict})
    edata = build_extracted_data([field])

    assert len(edata["groups"]) == len(field.data)
    for i in range(len(edata["groups"])):
        assert edata["groups"][i].order == field.data[i].key.set_index
        assert edata["groups"][i].order == field.data[i].value.set_index
        assert edata["groups"][i].elements[0] == field.data[i].id


def test_save_and_restore_edata_with_set_index__successful(extracted_data_service):
    fields = [
        SerializedExtractedField(**{"fieldPk": uuid4().hex, "data": data})
        for data in (
            string_data_dict_bbox_coordinates,
            kv_data_dict_bbox_coordinates,
            list_kv_data_dict,
            list_string_data_dict,
        )
    ]
    edata = build_extracted_data(fields)

    saved_edata = extracted_data_service.save_extracted_data(1, edata["fields"], edata["groups"])

    result = SerializedExtractedData.from_model(saved_edata)

    assert string_data_dict_bbox_coordinates["setIndex"] == result.fields[0].data.set_index
    assert kv_data_dict_bbox_coordinates["key"]["setIndex"] == result.fields[1].data.key.set_index
    assert kv_data_dict_bbox_coordinates["value"]["setIndex"] == result.fields[1].data.value.set_index
    for orig_data, result_data in zip(list_kv_data_dict, result.fields[2].data):
        assert orig_data["key"]["setIndex"] == result_data.key.set_index
        assert orig_data["value"]["setIndex"] == result_data.value.set_index
    for orig_data, result_data in zip(list_string_data_dict, result.fields[3].data):
        assert orig_data["setIndex"] == result_data.set_index
