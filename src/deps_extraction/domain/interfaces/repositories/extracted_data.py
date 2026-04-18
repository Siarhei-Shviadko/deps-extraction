from abc import ABC, abstractmethod

from deps_extracted_data import ExtractedData

from deps_extraction.domain.dtos import (
    ExtractedDataFilterObject,
    ExtractedDataListFilterObject,
)

__all__ = ["IExtractedDataRepository"]


class IExtractedDataRepository(ABC):
    @abstractmethod
    def save(self, extracted_data: ExtractedData) -> ExtractedData:
        pass

    @abstractmethod
    def find(self, document_id: int) -> ExtractedData:
        pass

    @abstractmethod
    def find_by_filter(self, filtering: ExtractedDataFilterObject) -> ExtractedData:
        pass

    @abstractmethod
    def delete(self, document_id: int) -> None:
        pass

    @abstractmethod
    def find_list_by_filter(self, filtering: ExtractedDataListFilterObject) -> list[ExtractedData]:
        pass

    @abstractmethod
    def find_with_internal_pagination(self, document_id: int, rows_per_chunk: int) -> ExtractedData:
        pass
