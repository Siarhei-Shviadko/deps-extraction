from typing import Any, Mapping

from deps_extraction.domain.model import FieldType, ListFieldDescription

from .base_types_mapping import BASE_TYPES_MAPPING
from .dict_description import DictDescriptionMapper
from .table_description import TableDescriptionMapper

__all__ = ["ListDescriptionMapper"]


LIST_DESCRIPTION_MAP = {  # noqa: WPS407
    **BASE_TYPES_MAPPING,
    FieldType.DICT: DictDescriptionMapper,
    FieldType.TABLE: TableDescriptionMapper,
}


class ListDescriptionMapper:
    @staticmethod
    def from_dict(raw_description: Mapping[str, Any]) -> ListFieldDescription:
        item_type = FieldType(raw_description["item_type"])
        item_type_class = LIST_DESCRIPTION_MAP[item_type]

        return ListFieldDescription(
            item_type=item_type,
            item_type_data=item_type_class.from_dict(raw_description["item_type_data"])
            if raw_description.get("item_type_data")
            else None,
        )

    @staticmethod
    def to_dict(description: ListFieldDescription) -> Mapping[str, Any]:
        item_type_class = LIST_DESCRIPTION_MAP[description.item_type]

        return {
            "item_type": description.item_type.value,
            "item_type_data": item_type_class.to_dict(description.item_type_data)
            if description.item_type_data
            else None,
        }
