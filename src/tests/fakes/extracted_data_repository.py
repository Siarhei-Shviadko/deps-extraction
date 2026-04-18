from typing import Any

from deps_extracted_data import ExtractedData

from deps_extraction.domain.dtos import (
    ExtractedDataFilterObject,
    ExtractedDataListFilterObject,
)
from deps_extraction.domain.exceptions import ExtractedDataNotFound
from deps_extraction.domain.interfaces import IExtractedDataRepository

__all__ = ["FakeExtractedDataRepository"]


class FakeExtractedDataRepository(IExtractedDataRepository):
    def __init__(self):
        self._db: dict[int, Any] = {}

    def save(self, extracted_data: ExtractedData) -> ExtractedData:
        self._db[extracted_data.document_id] = extracted_data
        return extracted_data

    def find(self, document_id: int) -> ExtractedData:
        try:
            return self._db[document_id]
        except KeyError:
            raise ExtractedDataNotFound(document_id)

    def find_by_filter(self, filtering: ExtractedDataFilterObject) -> ExtractedData:
        edata = self.find(filtering.document_id)
        if filtering.field_codes is not None:
            filtered = ExtractedData(edata.document_id)
            fields = [f for f in edata.fields if f.field_code in filtering.field_codes]
            filtered.add_extracted_fields(fields)
            return filtered
        return edata

    def delete(self, document_id: int) -> None:
        self._db.pop(document_id)

    def find_list_by_filter(self, filtering: ExtractedDataListFilterObject) -> list[ExtractedData]:
        pass

    def find_with_internal_pagination(self, document_id: int, rows_per_chunk: int) -> ExtractedData:
        return self.find(document_id)
