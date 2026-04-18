from typing import Optional, Union

from deps_extracted_data import FieldType, KeyValuePair
from deps_extracted_data.model.extracted_data.data_types import EntityId
from sqlalchemy.engine import RowProxy

from ..types import CommonDictType, ListOfDictsType
from .generic_data_mapper import GenericDataMapper

__all__ = ["KeyValuePairMapper"]


class KeyValuePairMapper:
    @staticmethod
    def to_dicts(kvp: KeyValuePair, index: Optional[str] = None, alias: Optional[str] = None) -> ListOfDictsType:
        key_data = GenericDataMapper().to_dict(kvp.key)
        key_data["index"] = f"{index}.key" if index else "key"
        key_data["field_type"] = FieldType.KEY_VALUE_PAIR.value

        value_data = GenericDataMapper().to_dict(kvp.value)
        value_data["index"] = f"{index}.value" if index else "value"
        value_data["field_type"] = FieldType.KEY_VALUE_PAIR.value

        kv_pair_data = {
            "id": kvp.id(),
            "index": f"{index}.kv_pair" if index else "kv_pair",
            "field_type": FieldType.KEY_VALUE_PAIR.value,
            "meta": {"alias": alias} if alias else None,
            "confidence": None,
            "value": None,
            "table_cell_coordinates": None,
            "source_bbox_coordinates": None,
            "source_table_coordinates": None,
            "source_text_coordinates": None,
        }
        return [kv_pair_data, key_data, value_data]

    @staticmethod
    def from_dicts(raw_data: list[Union[RowProxy, CommonDictType]]) -> KeyValuePair:
        for field in raw_data:
            index = field["index"].split(".")[-1]
            if index == "key":
                key = GenericDataMapper().from_dict(field)
            elif index == "value":
                value = GenericDataMapper().from_dict(field)
            elif index == "kv_pair":
                id_ = EntityId(field["id"])

        return KeyValuePair(key=key, value=value, id_=id_)
