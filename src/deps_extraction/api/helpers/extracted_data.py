from typing import Any, Optional

from deps_extracted_data.model.extracted_data import ExtractedField, FieldData, Group
from deps_extracted_data.serializers import SerializedGroup
from deps_extracted_data.serializers.v1 import (
    FieldDataType,
    SerializedDictFieldData,
    SerializedExtractedField,
)

__all__ = ["build_extracted_data"]


def build_extracted_data(extracted_fields: list[SerializedExtractedField]) -> dict[str, Any]:
    fields = [field.to_model() for field in extracted_fields]
    groups = _get_groups_from_fields(extracted_fields, fields)

    return {"fields": fields, "groups": groups}


def _get_groups_from_fields(  # noqa: WPS231
    raw_fields: list[SerializedExtractedField],
    model_fields: list[ExtractedField],
) -> list[Group]:
    groups = []
    for raw_field, model_field in zip(raw_fields, model_fields):
        if isinstance(raw_field.data, list):
            for raw_el, model_el in zip(raw_field.data, model_field.data.elements):
                if group := _build_group_from_data(raw_el, model_el):
                    groups.append(group.to_model())
        elif group := _build_group_from_data(raw_field.data, model_field.data):
            groups.append(group.to_model())
    return groups


def _build_group_from_data(raw_data: FieldDataType, model_data: FieldData) -> Optional[SerializedGroup]:
    if isinstance(raw_data, SerializedDictFieldData):
        key_index = raw_data.key.set_index
        value_index = raw_data.value.set_index
        if any(el is not None for el in (key_index, value_index)):
            return SerializedGroup(
                order=key_index or value_index,
                name=str(key_index or value_index),
                elements=[model_data.id()],
            )
        return None
    return (
        SerializedGroup(order=raw_data.set_index, name=str(raw_data.set_index), elements=[model_data.id()])
        if raw_data.set_index is not None
        else None
    )
