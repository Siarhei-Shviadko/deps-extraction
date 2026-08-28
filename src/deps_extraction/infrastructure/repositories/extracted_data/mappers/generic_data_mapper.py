from typing import Optional, Union

from deps_extracted_data import (
    CheckboxValue,
    Data,
    ExtractedDataValueType,
    FieldType,
    GenericData,
)
from deps_extracted_data.model.extracted_data.data_types import EntityId
from sqlalchemy.engine import RowMapping

from deps_extraction.domain.exceptions import (
    UnknownExtractedDataValueType,
    UnknownFieldType,
)

from ..types import CommonDictType
from .bbox_coordinates_mappers import (
    build_dict_from_source_bbox_coordinates,
    build_source_bbox_coordinates_from_dict,
)
from .table_coordinates_mappers import SourceTableCoordinatesMapper
from .text_coordinates_mappers import SourceTextCoordinatesMapper
from .utils import build_dict_for_meta_column_from

__all__ = ["GenericDataMapper"]


class GenericDataMapper:
    def to_dict(self, data: GenericData, index: Optional[str] = None, alias: Optional[str] = None) -> CommonDictType:
        field_type = self._get_field_type_by_value(data.value)
        value_type = self._get_value_type(data.value)

        return {
            "id": data.id(),
            "field_type": field_type.value,
            "meta": build_dict_for_meta_column_from(keys=("value_type", "alias"), values=(value_type.value, alias)),
            "index": index if index else "",
            "value": getattr(data.value, "mapped_value", data.value),
            "confidence": data.confidence,
            "table_cell_coordinates": None,
            "source_bbox_coordinates": build_dict_from_source_bbox_coordinates(data.source_bbox_coordinates),
            "source_table_coordinates": SourceTableCoordinatesMapper.to_dict(data.source_table_coordinates),
            "source_text_coordinates": SourceTextCoordinatesMapper.to_dict(data.source_text_coordinates),
        }

    def from_dict(self, raw_data: Union[RowMapping, CommonDictType]) -> GenericData:
        value = self._get_value_by_type(raw_data)
        data = GenericData(
            value=value,
            confidence=raw_data["confidence"],
            id_=EntityId(raw_data["id"]),
        )
        source_bbox_coordinates = build_source_bbox_coordinates_from_dict(raw_data["source_bbox_coordinates"])
        if source_bbox_coordinates is not None:
            data.source_bbox_coordinates = source_bbox_coordinates
        source_table_coordinates = SourceTableCoordinatesMapper.from_dict(raw_data["source_table_coordinates"])
        if source_table_coordinates is not None:
            data.source_table_coordinates = source_table_coordinates
        source_text_coordinates = SourceTextCoordinatesMapper.from_dict(raw_data["source_text_coordinates"])
        if source_text_coordinates is not None:
            data.source_text_coordinates = source_text_coordinates
        return data

    @staticmethod
    def _get_field_type_by_value(value: Data) -> FieldType:
        if isinstance(value, str):
            return FieldType.STRING
        elif isinstance(value, bool):
            return FieldType.CHECKBOX
        elif isinstance(value, CheckboxValue):
            return FieldType.CHECKBOX
        raise UnknownFieldType()

    @staticmethod
    def _get_value_by_type(raw_data: Union[RowMapping, CommonDictType]) -> Data:
        value_type = raw_data["meta"]["value_type"]
        if value_type == ExtractedDataValueType.STRING.value:
            return raw_data["value"]
        elif value_type == ExtractedDataValueType.CHECKBOX.value:
            value = raw_data["value"]
            value = value if value is None else value.lower() == "true"
            return CheckboxValue.create(value)
        raise UnknownExtractedDataValueType()

    @staticmethod
    def _get_value_type(value: Data) -> ExtractedDataValueType:
        if isinstance(value, str):
            return ExtractedDataValueType.STRING
        elif isinstance(value, CheckboxValue):
            return ExtractedDataValueType.CHECKBOX
        raise UnknownExtractedDataValueType()
