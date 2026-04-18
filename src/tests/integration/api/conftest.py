import copy
import random
import uuid
from itertools import chain
from typing import Any

import pytest

from deps_extraction.api import auth
from tests.data.extracted_data import (
    checkmark_data_dict_bbox_coordinates,
    checkmark_data_dict_table_coordinates,
    checkmark_data_dict_text_coordinates,
    checkmark_data_dict_without_id,
    empty_list,
    kv_data_dict_bbox_coordinates,
    kv_data_dict_table_coordinates,
    kv_data_dict_text_coordinates,
    kv_data_dict_without_id,
    list_checkmark_data_dict,
    list_checkmark_data_dict_without_id,
    list_kv_data_dict,
    list_kv_data_dict_without_id,
    list_string_data_dict,
    list_string_data_dict_without_id,
    list_table_data_dict,
    list_table_data_dict_without_id,
    string_data_dict_bbox_coordinates,
    string_data_dict_table_coordinates,
    string_data_dict_text_coordinates,
    string_data_dict_without_coordinates,
    string_data_dict_without_id,
    table_data_dict_bbox_coordinates,
    table_data_dict_table_coordinates,
    table_data_dict_text_coordinates_for_cells,
    table_data_dict_without_id,
)
from tests.data.groups import group_dict
from tests.factories import GroupFactory


@pytest.fixture(autouse=True)
def mocked_middleware(monkeypatch, mocker):
    monkeypatch.setattr(auth, "set_user_from_token", mocker.Mock({}))


@pytest.fixture
def saved_extracted_data(extracted_data_factory, extracted_data_repository):
    edata = extracted_data_factory()
    extracted_data_repository.save(edata)
    return edata


@pytest.fixture(
    params=(
        empty_list,
        string_data_dict_without_coordinates,
        string_data_dict_bbox_coordinates,
        string_data_dict_text_coordinates,
        string_data_dict_table_coordinates,
        list_string_data_dict,
        kv_data_dict_bbox_coordinates,
        kv_data_dict_table_coordinates,
        kv_data_dict_text_coordinates,
        list_kv_data_dict,
        table_data_dict_bbox_coordinates,
        table_data_dict_table_coordinates,
        table_data_dict_text_coordinates_for_cells,
        list_table_data_dict,
        checkmark_data_dict_bbox_coordinates,
        checkmark_data_dict_table_coordinates,
        checkmark_data_dict_text_coordinates,
        list_checkmark_data_dict,
    )
)
def extracted_data_dict(request):
    field_data = request.param
    edata_dict = {"fieldPk": uuid.uuid4().hex, "data": field_data if isinstance(field_data, list) else [field_data]}
    return [edata_dict]


@pytest.fixture(
    params=(
        empty_list,
        string_data_dict_without_coordinates,
        string_data_dict_bbox_coordinates,
        string_data_dict_text_coordinates,
        string_data_dict_table_coordinates,
        list_string_data_dict,
        kv_data_dict_bbox_coordinates,
        kv_data_dict_table_coordinates,
        kv_data_dict_text_coordinates,
        list_kv_data_dict,
        table_data_dict_bbox_coordinates,
        table_data_dict_table_coordinates,
        table_data_dict_text_coordinates_for_cells,
        list_table_data_dict,
        checkmark_data_dict_bbox_coordinates,
        checkmark_data_dict_table_coordinates,
        checkmark_data_dict_text_coordinates,
        list_checkmark_data_dict,
    )
)
def extracted_data_dict_v2(request):
    field_data = request.param
    edata_dict = {"fieldCode": uuid.uuid4().hex, "data": field_data if isinstance(field_data, list) else [field_data]}
    groups = random.choice((None, [], _create_group(field_data)))
    return {
        "fields": [edata_dict],
        "groups": groups,
    }


@pytest.fixture(
    params=(
        [
            (
                empty_list,
                string_data_dict_bbox_coordinates,
                string_data_dict_text_coordinates,
                string_data_dict_table_coordinates,
                list_string_data_dict,
                kv_data_dict_bbox_coordinates,
                kv_data_dict_table_coordinates,
                kv_data_dict_text_coordinates,
                list_kv_data_dict,
                table_data_dict_bbox_coordinates,
                table_data_dict_table_coordinates,
                table_data_dict_text_coordinates_for_cells,
                list_table_data_dict,
                checkmark_data_dict_bbox_coordinates,
                checkmark_data_dict_table_coordinates,
                checkmark_data_dict_text_coordinates,
                list_checkmark_data_dict,
            )
        ]
    )
)
def extracted_data_dict_with_several_fields(request):
    def create_edata_dict(field_data):
        return {"fieldPk": uuid.uuid4().hex, "data": field_data}

    field_data = random.sample(request.param, k=random.randint(2, 5))
    edata_dict = [create_edata_dict(fd) for fd in field_data]
    return edata_dict


@pytest.fixture(
    params=(
        [
            (
                empty_list,
                string_data_dict_bbox_coordinates,
                string_data_dict_text_coordinates,
                string_data_dict_table_coordinates,
                list_string_data_dict,
                kv_data_dict_bbox_coordinates,
                kv_data_dict_table_coordinates,
                kv_data_dict_text_coordinates,
                list_kv_data_dict,
                table_data_dict_bbox_coordinates,
                table_data_dict_table_coordinates,
                table_data_dict_text_coordinates_for_cells,
                list_table_data_dict,
                checkmark_data_dict_bbox_coordinates,
                checkmark_data_dict_table_coordinates,
                checkmark_data_dict_text_coordinates,
                list_checkmark_data_dict,
            )
        ]
    )
)
def extracted_data_dict_with_several_fields_v2(request):
    def create_edata_dict(field_data):
        return {"fieldCode": uuid.uuid4().hex, "data": field_data}

    field_data = random.sample(request.param, k=random.randint(2, 5))
    edata_dict = [create_edata_dict(fd) for fd in field_data]
    groups = random.choice(
        [
            None,
            [],
            list(
                chain.from_iterable(
                    [
                        _create_group(el)
                        for el in field_data[: random.randint(2, len(field_data))]
                        if not isinstance(el, list)
                    ]
                )
            ),
        ]
    )
    return {"fields": edata_dict, "groups": groups}


def _create_group(field_data):
    element_id = None
    if isinstance(field_data, list):
        if field_data:
            element_id = random.choice([el["id"] for el in field_data])
        else:
            return
    group = GroupFactory()
    group.add_element(field_data["id"] if element_id is None else element_id)
    return [group_dict(group)]


@pytest.fixture(
    params=(
        [
            (
                empty_list,
                string_data_dict_bbox_coordinates,
                string_data_dict_text_coordinates,
                string_data_dict_table_coordinates,
                list_string_data_dict,
                kv_data_dict_bbox_coordinates,
                kv_data_dict_table_coordinates,
                kv_data_dict_text_coordinates,
                list_kv_data_dict,
                table_data_dict_bbox_coordinates,
                table_data_dict_table_coordinates,
                table_data_dict_text_coordinates_for_cells,
                list_table_data_dict,
                checkmark_data_dict_bbox_coordinates,
                checkmark_data_dict_table_coordinates,
                checkmark_data_dict_text_coordinates,
                list_checkmark_data_dict,
            )
        ]
    )
)
def extracted_data_dict_with_all_fields_and_groups(request):
    def create_edata_dict(field_data):
        return {"fieldCode": uuid.uuid4().hex, "data": field_data}

    field_data = request.param
    edata_dict = [create_edata_dict(fd) for fd in field_data]
    groups = [GroupFactory() for _ in range(5)]
    for el in field_data:
        if isinstance(el, list):
            el and random.choice(groups).add_element(random.choice(el)["id"])
        else:
            random.choice(groups).add_element(el["id"])

    return {"fields": edata_dict, "groups": [group_dict(group) for group in groups]}


@pytest.fixture(
    params=(
        [
            (
                string_data_dict_without_id,
                kv_data_dict_without_id,
                table_data_dict_without_id,
                checkmark_data_dict_without_id,
                list_string_data_dict_without_id,
                list_kv_data_dict_without_id,
                list_table_data_dict_without_id,
                list_checkmark_data_dict_without_id,
            )
        ]
    )
)
def extracted_data_dict_with_fields_without_id(request):
    def create_edata_dict(field_data):
        return {"fieldPk": uuid.uuid4().hex, "data": field_data}

    field_data = request.param
    edata_dict = [create_edata_dict(fd) for fd in field_data]
    return edata_dict


@pytest.fixture(
    params=(
        [
            (
                empty_list,
                string_data_dict_bbox_coordinates,
                string_data_dict_text_coordinates,
                string_data_dict_table_coordinates,
                list_string_data_dict,
                kv_data_dict_bbox_coordinates,
                kv_data_dict_table_coordinates,
                kv_data_dict_text_coordinates,
                list_kv_data_dict,
                table_data_dict_bbox_coordinates,
                table_data_dict_table_coordinates,
                table_data_dict_text_coordinates_for_cells,
                list_table_data_dict,
                checkmark_data_dict_bbox_coordinates,
                checkmark_data_dict_table_coordinates,
                checkmark_data_dict_text_coordinates,
                list_checkmark_data_dict,
            )
        ]
    )
)
def extracted_data_dict_with_all_fields_and_set_indexes(request):
    def create_edata_dict(field_data):
        return {"fieldPk": uuid.uuid4().hex, "data": field_data}

    field_data = request.param
    edata_dict = [create_edata_dict(fd) for fd in field_data]

    return edata_dict


@pytest.fixture
def extracted_data_table_field_with_invalid_cell_table_coordinates():
    data = copy.deepcopy(table_data_dict_bbox_coordinates)
    data["cells"][0]["coordinates"] = data["cells"][1]["coordinates"]

    return [{"fieldPk": uuid.uuid4().hex, "data": data}]


@pytest.fixture
def extracted_data_table_field_with_invalid_cell_table_coordinates_v2():
    data = copy.deepcopy(table_data_dict_bbox_coordinates)
    data["cells"][0]["coordinates"] = data["cells"][1]["coordinates"]

    return {"fields": [{"fieldPk": uuid.uuid4().hex, "data": data}], "groups": []}


@pytest.fixture(
    params=(
        [
            (
                empty_list,
                string_data_dict_bbox_coordinates,
                string_data_dict_text_coordinates,
                string_data_dict_table_coordinates,
                list_string_data_dict,
                kv_data_dict_bbox_coordinates,
                kv_data_dict_table_coordinates,
                kv_data_dict_text_coordinates,
                list_kv_data_dict,
                table_data_dict_bbox_coordinates,
                table_data_dict_table_coordinates,
                table_data_dict_text_coordinates_for_cells,
                list_table_data_dict,
                checkmark_data_dict_bbox_coordinates,
                checkmark_data_dict_table_coordinates,
                checkmark_data_dict_text_coordinates,
                list_checkmark_data_dict,
            )
        ]
    )
)
def extracted_data_dict_with_several_fields_and_aliases_v2(request):
    def create_edata_dict(field_data):
        if isinstance(field_data, list):
            return {"fieldCode": uuid.uuid4().hex, "data": field_data, "aliases": make_aliases_from(field_data)}
        return {"fieldCode": uuid.uuid4().hex, "data": field_data}

    field_data = request.param
    edata_dict = [create_edata_dict(fd) for fd in field_data]
    groups = random.choice(
        [
            None,
            [],
            list(
                chain.from_iterable(
                    [
                        _create_group(el)
                        for el in field_data[: random.randint(2, len(field_data))]
                        if not isinstance(el, list)
                    ]
                )
            ),
        ]
    )
    return {"fields": edata_dict, "groups": groups}


@pytest.fixture(
    params=(
        [
            (
                empty_list,
                string_data_dict_bbox_coordinates,
                string_data_dict_text_coordinates,
                string_data_dict_table_coordinates,
                list_string_data_dict,
                kv_data_dict_bbox_coordinates,
                kv_data_dict_table_coordinates,
                kv_data_dict_text_coordinates,
                list_kv_data_dict,
                table_data_dict_bbox_coordinates,
                table_data_dict_table_coordinates,
                table_data_dict_text_coordinates_for_cells,
                list_table_data_dict,
                checkmark_data_dict_bbox_coordinates,
                checkmark_data_dict_table_coordinates,
                checkmark_data_dict_text_coordinates,
                list_checkmark_data_dict,
            )
        ]
    )
)
def extracted_data_dict_with_several_fields_and_aliases(request):
    def create_edata_dict(field_data):
        if isinstance(field_data, list):
            return {"fieldPk": uuid.uuid4().hex, "data": field_data, "aliases": make_aliases_from(field_data)}
        return {"fieldPk": uuid.uuid4().hex, "data": field_data}

    edata_dict = [create_edata_dict(fd) for fd in request.param]
    return edata_dict


def make_aliases_from(data: list[dict[str, Any]]) -> dict[str, str]:
    return {el["id"]: uuid.uuid4().hex for el in data}
