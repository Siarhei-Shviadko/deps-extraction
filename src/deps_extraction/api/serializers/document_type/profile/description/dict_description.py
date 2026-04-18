from typing import Optional

from pydantic import Field

from deps_extraction.domain.model import DictFieldDescription, FieldType

from ....configured_base_serializer import ConfiguredBaseSerializer
from .type_mapping import GENERIC_DESCRIPTION_MAP, DescriptionGenericType

__all__ = ["SerializedDictDescription"]


class SerializedDictDescription(ConfiguredBaseSerializer):
    key_type: FieldType = Field(alias="keyType")
    key_data: Optional[DescriptionGenericType] = Field(None, alias="keyMeta")
    value_type: FieldType = Field(alias="valueType")
    value_data: Optional[DescriptionGenericType] = Field(None, alias="valueMeta")

    def to_model(self) -> DictFieldDescription:
        return DictFieldDescription(
            key_type=self.key_type,
            value_type=self.value_type,
            key_meta=self.key_data.to_model() if self.key_data else None,
            value_meta=self.value_data.to_model() if self.value_data else None,
        )

    @classmethod
    def from_model(cls, description: DictFieldDescription) -> "SerializedDictDescription":
        key_data_serializer = GENERIC_DESCRIPTION_MAP.get(description.key_meta.__class__)
        serialized_key_data = key_data_serializer.from_model(description.key_meta) if key_data_serializer else None

        value_data_serializer = GENERIC_DESCRIPTION_MAP.get(description.value_meta.__class__)
        serialized_value_data = (
            value_data_serializer.from_model(description.value_meta) if value_data_serializer else None
        )

        return cls(
            key_type=description.key_type,
            key_data=serialized_key_data,
            value_type=description.value_type,
            value_data=serialized_value_data,
        )
