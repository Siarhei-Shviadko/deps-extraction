from deps_extracted_data import ExtractedData, FieldType
from sqlalchemy.engine import RowMapping

from deps_extraction.domain.exceptions import UnknownFieldType

from ..types import CommonDictType
from .extracted_field_mapper import ExtractedFieldMapper
from .group_mapper import GroupMapper

FIRST_ELEMENT: int = 0

__all__ = ["ExtractedDataMapper"]


class ExtractedDataMapper:
    @staticmethod
    def to_dicts(edata: ExtractedData) -> CommonDictType:
        edata_fields = []
        for field in edata.fields:
            field_dicts = ExtractedFieldMapper.to_dicts(field)
            for field_dict in field_dicts:
                field_dict["document_id"] = edata.document_id
                edata_fields.append(field_dict)
        groups = GroupMapper.to_dict(edata)
        return {"fields": edata_fields, "groups": groups}

    def from_dicts(self, raw_edata: list[RowMapping]) -> ExtractedData:
        edata = ExtractedData(raw_edata[FIRST_ELEMENT]["document_id"])
        groups = raw_edata[FIRST_ELEMENT]["groups"]
        field_code = None
        field_rows: list[RowMapping] = []

        for rd in raw_edata:  # noqa: WPS500
            if field_code is None:
                field_code = rd["field_code"]
            if rd["field_code"] != field_code:
                self._add_field_to_edata(edata, field_rows)
                field_code = rd["field_code"]
                field_rows = []
            field_rows.append(rd)
        else:
            self._add_field_to_edata(edata, field_rows)

        if groups:
            edata.add_groups([GroupMapper.from_dict(group) for group in groups])

        return edata

    def edata_list_from_dicts(self, edata: list[RowMapping]) -> list[ExtractedData]:
        document_id = None
        field_rows: list[RowMapping] = []
        edatas = []
        for row in edata:  # noqa: WPS500
            if document_id is None:
                document_id = row["document_id"]
            if row["document_id"] != document_id:
                edatas.append(self.from_dicts(field_rows))
                document_id = row["document_id"]
                field_rows = []
            field_rows.append(row)
        else:
            edatas.append(self.from_dicts(field_rows))

        return edatas

    @staticmethod
    def _add_field_to_edata(edata: ExtractedData, field_rows: list[RowMapping]) -> None:
        field = ExtractedFieldMapper.from_dicts(field_rows)
        field_type = field_rows[FIRST_ELEMENT]["field_type"]
        if field_type == FieldType.STRING.value:
            return edata.add_string(field)
        elif field_type == FieldType.CHECKBOX.value:
            return edata.add_checkbox(field)
        elif field_type == FieldType.KEY_VALUE_PAIR.value:
            return edata.add_key_value_pair(field)
        elif field_type == FieldType.TABLE.value:
            return edata.add_table(field)
        elif field_type == FieldType.STRING_LIST.value:
            return edata.add_string_list(field)
        elif field_type == FieldType.TABLE_LIST.value:
            return edata.add_table_list(field)
        elif field_type == FieldType.KEY_VALUE_PAIR_LIST.value:
            return edata.add_key_value_pair_list(field)
        raise UnknownFieldType()
