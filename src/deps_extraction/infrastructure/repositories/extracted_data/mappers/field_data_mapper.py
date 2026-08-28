from collections import defaultdict
from typing import Any, Optional, Union

from deps_extracted_data import (
    ElementType,
    EntityId,
    FieldData,
    FieldType,
    GenericData,
    GenericList,
    KeyValuePair,
    Table,
)
from sqlalchemy.engine import RowMapping

from deps_extraction.domain.exceptions import UnknownFieldType

from ..types import CommonDictType, ListOfDictsType
from .generic_data_mapper import GenericDataMapper
from .key_value_pair_mapper import KeyValuePairMapper
from .table_mappers import TableMapper

FIRST_ELEMENT: int = 0
FIELD_LIST_TYPES = frozenset(
    (
        FieldType.KEY_VALUE_PAIR_LIST.value,
        FieldType.STRING_LIST.value,
        FieldType.KEY_VALUE_PAIR_LIST.value,
        FieldType.TABLE_LIST.value,
    ),
)

__all__ = ["FieldDataMapper"]


class FieldDataMapper:
    def to_dicts(self, data: FieldData, index: Optional[str] = None, alias: Optional[str] = None) -> ListOfDictsType:
        if isinstance(data, GenericList):
            list_of_dicts = []
            for num, ex_data in enumerate(data.elements):
                list_item_dicts = self.to_dicts(ex_data, index=str(num), alias=data.aliases.get(ex_data.id))
                self._set_types_by_element_type(list_item_dicts, ex_data)
                list_of_dicts.extend(list_item_dicts)
            return list_of_dicts

        if isinstance(data, Table):
            return TableMapper().to_dicts(data, index, alias)
        elif isinstance(data, GenericData):
            return [GenericDataMapper().to_dict(data, index, alias)]
        elif isinstance(data, KeyValuePair):
            return KeyValuePairMapper.to_dicts(data, index, alias)
        raise UnknownFieldType()

    def from_dicts(self, raw_data: list[Union[RowMapping, CommonDictType]]) -> FieldData:
        field_type = raw_data[FIRST_ELEMENT]["field_type"]
        if field_type in {FieldType.STRING.value, FieldType.CHECKBOX.value}:
            return GenericDataMapper().from_dict(raw_data[FIRST_ELEMENT])
        elif field_type == FieldType.KEY_VALUE_PAIR.value:
            return KeyValuePairMapper().from_dicts(raw_data)
        elif field_type == FieldType.TABLE.value:
            return TableMapper().from_dicts(raw_data)
        elif field_type in FIELD_LIST_TYPES:
            sorted_raw_data = sorted(
                raw_data,
                key=lambda x: int(x["index"].split(".")[FIRST_ELEMENT]),
            )
            data_split_by_list_index: CommonDictType = defaultdict(list)
            field_type = self._get_filed_type(raw_data[FIRST_ELEMENT])
            aliases = {}
            for data in sorted_raw_data:
                data = dict(data)
                data["field_type"] = field_type.value
                list_index = data["index"].split(".")[FIRST_ELEMENT]
                data_split_by_list_index[list_index].append(data)

                if (alias := self._find_alias(data)) is not None:
                    aliases.update(alias)

            elements = [self.from_dicts(split_data) for split_data in data_split_by_list_index.values()]

            return GenericList(elements=elements, aliases=aliases)
        raise UnknownFieldType()

    def _set_types_by_element_type(self, element_dicts: ListOfDictsType, data: ElementType) -> None:
        list_type = self._get_list_type(data)
        for element_dict in element_dicts:
            element_dict["field_type"] = list_type.value

    @staticmethod
    def _get_list_type(data: ElementType) -> FieldType:
        if isinstance(data, Table):
            return FieldType.TABLE_LIST
        elif isinstance(data, GenericData):
            return FieldType.STRING_LIST
        elif isinstance(data, KeyValuePair):
            return FieldType.KEY_VALUE_PAIR_LIST
        raise UnknownFieldType()

    @staticmethod
    def _get_filed_type(data: CommonDictType) -> FieldType:
        field_type = data["field_type"]
        if field_type == FieldType.TABLE_LIST.value:
            return FieldType.TABLE
        elif field_type == FieldType.STRING_LIST.value:
            return FieldType.STRING
        elif field_type == FieldType.KEY_VALUE_PAIR_LIST.value:
            return FieldType.KEY_VALUE_PAIR
        raise UnknownFieldType()

    @staticmethod
    def _aliases_to_dict(aliases: dict[EntityId, str]) -> dict[str, str]:
        return {element_id(): alias for element_id, alias in aliases.items()}

    @staticmethod
    def _find_alias(data: dict[str, Any]) -> Optional[dict[EntityId, str]]:
        if (meta := data.get("meta")) is not None and (alias := meta.get("alias")) is not None:
            return {EntityId(data["id"]): alias}
