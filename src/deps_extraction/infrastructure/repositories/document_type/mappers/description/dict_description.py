from typing import Any, Mapping

from deps_extraction.domain.model import DictFieldDescription, FieldType

from .base_types_mapping import BASE_TYPES_MAPPING

__all__ = ["DictDescriptionMapper"]


class DictDescriptionMapper:
    @staticmethod
    def from_dict(raw_description: Mapping[str, Any]) -> DictFieldDescription:
        key_type = FieldType(raw_description["key_type"])
        key_type_class = BASE_TYPES_MAPPING[key_type]

        value_type = FieldType(raw_description["value_type"])
        value_type_class = BASE_TYPES_MAPPING[value_type]

        return DictFieldDescription(
            key_type=key_type,
            key_meta=key_type_class.from_dict(raw_description["key_meta"]) if raw_description.get("key_meta") else None,
            value_type=value_type,
            value_meta=value_type_class.from_dict(raw_description["value_meta"])
            if raw_description.get("value_meta")
            else None,
        )

    @staticmethod
    def to_dict(description: DictFieldDescription) -> Mapping[str, Any]:
        key_meta_class = BASE_TYPES_MAPPING[description.key_type]
        value_meta_class = BASE_TYPES_MAPPING[description.value_type]

        return {
            "key_type": description.key_type.value,
            "key_meta": key_meta_class.to_dict(description.key_meta) if description.key_meta else None,
            "value_type": description.value_type.value,
            "value_meta": value_meta_class.to_dict(description.value_meta) if description.value_meta else None,
        }
