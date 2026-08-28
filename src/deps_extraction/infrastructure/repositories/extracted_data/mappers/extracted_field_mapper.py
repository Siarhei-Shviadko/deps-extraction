from deps_extracted_data import ExtractedField
from sqlalchemy.engine import RowMapping

from ..types import ListOfDictsType
from .field_data_mapper import FieldDataMapper

FIRST_ELEMENT: int = 0

__all__ = ["ExtractedFieldMapper"]


class ExtractedFieldMapper:
    @staticmethod
    def to_dicts(ex_field: ExtractedField) -> ListOfDictsType:
        return [
            {
                "field_code": ex_field.field_code,
                **field_data,
            }
            for field_data in FieldDataMapper().to_dicts(ex_field.data)
        ]

    @staticmethod
    def from_dicts(raw_field: list[RowMapping]) -> ExtractedField:
        data = FieldDataMapper().from_dicts(raw_field)
        return ExtractedField(field_code=raw_field[FIRST_ELEMENT]["field_code"], data=data)
