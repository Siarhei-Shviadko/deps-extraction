from typing import Optional, Union

from pydantic import Field, model_validator

from deps_extraction.domain.model import (
    DictFieldDescription,
    FieldType,
    ListFieldDescription,
    TableFieldDescription,
)

from ....configured_base_serializer import ConfiguredBaseSerializer
from .date_description import SerializedDateDescription
from .dict_description import SerializedDictDescription
from .enum_description import SerializedEnumDescription
from .string_description import SerializedStringDescription
from .table_description import SerializedTableDescription
from .type_mapping import GENERIC_DESCRIPTION_MAP

__all__ = ["SerializedListDescription"]


SerializedBaseTypeDescription = Union[
    SerializedTableDescription,
    SerializedEnumDescription,
    SerializedDictDescription,
    SerializedDateDescription,
    SerializedStringDescription,
]


LIST_DESCRIPTION_MAP = {  # noqa: WPS407
    **GENERIC_DESCRIPTION_MAP,
    TableFieldDescription: SerializedTableDescription,
    DictFieldDescription: SerializedDictDescription,
}


LIST_BASE_TYPE_SERIALIZER_MAP = {  # noqa: WPS407
    FieldType.STRING: SerializedStringDescription,
    FieldType.CHECKMARK: SerializedStringDescription,
    FieldType.ENUM: SerializedEnumDescription,
    FieldType.DATE: SerializedDateDescription,
    FieldType.DICT: SerializedDictDescription,
    FieldType.TABLE: SerializedTableDescription,
}


class SerializedListDescription(ConfiguredBaseSerializer):
    base_type: FieldType = Field(alias="baseType")
    base_type_data: Optional[SerializedBaseTypeDescription] = Field(None, alias="baseTypeMeta")

    @model_validator(mode="after")
    def validate_base_type_meta(self) -> "SerializedListDescription":
        if self.base_type_data is None:
            return self

        expected_serializer = LIST_BASE_TYPE_SERIALIZER_MAP.get(self.base_type)
        if expected_serializer is None:
            raise ValueError(f"Unsupported baseType: {self.base_type}")

        if not isinstance(self.base_type_data, expected_serializer):
            raise ValueError(f"baseTypeMeta is not valid for baseType '{self.base_type.value}'")

        return self

    def to_model(self) -> ListFieldDescription:
        return ListFieldDescription(
            item_type=self.base_type,
            item_type_data=self.base_type_data.to_model() if self.base_type_data else None,
        )

    @classmethod
    def from_model(cls, description: ListFieldDescription) -> "SerializedListDescription":
        base_type_serializer = LIST_DESCRIPTION_MAP.get(description.item_type_data.__class__)
        serialized_base_type = (
            base_type_serializer.from_model(description.item_type_data) if base_type_serializer else None
        )

        return cls(
            base_type=description.item_type,
            base_type_data=serialized_base_type,
        )
