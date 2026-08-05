import logging

from deps_extracted_data import EntityId, ExtractedData
from deps_extracted_data.model import ExtractedDataFactory
from deps_extracted_data.model.extracted_data import ExtractedField, Group
from deps_message_flow.events.publisher import DomainEventPublisher

from deps_extraction.domain.dtos import (
    ExtractedDataFilterObject,
    ExtractedDataListFilterObject,
)
from deps_extraction.domain.exceptions import (
    ExtractedDataNotFound,
    ExtractedFieldNotFound,
    ExtractedFieldUpdateAliasesError,
)
from deps_extraction.domain.interfaces import IExtractedDataRepository

__all__ = ["ExtractedDataService"]


class ExtractedDataService:
    AGGREGATE_TYPE = "ExtractedData"

    def __init__(
        self,
        domain_event_publisher: DomainEventPublisher,
        extracted_data_repository: IExtractedDataRepository,
    ):
        self._domain_event_publisher = domain_event_publisher
        self._extracted_data_repository = extracted_data_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_extracted_data(self, document_id: int) -> ExtractedData:
        return self._extracted_data_repository.find(document_id)

    def get_extracted_fields_by_filter(self, filtering: ExtractedDataFilterObject) -> list[ExtractedField]:
        extracted_data = self._extracted_data_repository.find_by_filter(filtering)
        found_codes = {field.field_code for field in extracted_data.fields}
        missing_codes = set(filtering.field_codes) - found_codes
        if missing_codes:
            raise ExtractedFieldNotFound(list(missing_codes))
        return extracted_data.fields

    def get_paginated_extract_data(self, document_id: int, rows_per_chunk: int) -> ExtractedData:
        return self._extracted_data_repository.find_with_internal_pagination(document_id, rows_per_chunk)

    def save_extracted_data(
        self,
        document_id: int,
        extracted_fields: list[ExtractedField],
        groups: list[Group],
    ) -> ExtractedData:
        extracted_data = self._find_or_create_extracted_data(document_id)

        for field in extracted_fields:
            extracted_data.save_extracted_field(field)

        extracted_data.add_groups(groups)

        return self._extracted_data_repository.save(extracted_data)

    def save_extracted_data_with_override(
        self,
        document_id: int,
        extracted_fields: list[ExtractedField],
        groups: list[Group],
    ) -> ExtractedData:
        extracted_data = self._find_or_create_extracted_data(document_id)
        extracted_data.replace_fields_with(extracted_fields)
        extracted_data.add_groups(groups)

        return self._extracted_data_repository.save(extracted_data)

    def delete_extracted_data(self, document_id: int) -> None:
        self._extracted_data_repository.delete(document_id)

    def get_extracted_data_list_by_filter(self, filtering: ExtractedDataListFilterObject) -> list[ExtractedData]:
        return self._extracted_data_repository.find_list_by_filter(filtering)

    def save_field(self, document_id: int, field: ExtractedField) -> ExtractedField:
        extracted_data = self._find_or_create_extracted_data(document_id)
        extracted_data.save_extracted_field(field)
        edata = self._extracted_data_repository.save(extracted_data)
        self._publish_events(extracted_data)

        return edata.get(field.field_code)

    def delete_extracted_fields(self, document_id: int, field_codes: list[str]) -> None:
        edata = self._extracted_data_repository.find(document_id)
        edata.delete_fields_by_code(field_codes)
        self._extracted_data_repository.save(edata)
        self._publish_events(edata)

    def update_aliases(self, document_id: int, field_code: str, aliases: dict[str, str]) -> None:
        edata = self._extracted_data_repository.find(document_id=document_id)
        try:
            edata.update_field_aliases(
                field_code=field_code,
                aliases={EntityId(element_id): alias for element_id, alias in aliases.items()},
            )
            self._extracted_data_repository.save(edata)
        except RuntimeError:
            self._logger.error(
                "Error in time of updating document: <%s>, field_code: <%s> with aliases: <%s>",
                document_id,
                field_code,
                aliases,
            )
            raise ExtractedFieldUpdateAliasesError(f"Aliases can't be set up for field with code: <{field_code}>")

    def _find_or_create_extracted_data(self, document_id):
        try:
            extracted_data = self._extracted_data_repository.find(document_id)
        except ExtractedDataNotFound:
            extracted_data = ExtractedDataFactory.make_extracted_data(document_id=document_id)

        return extracted_data

    def _publish_events(self, extracted_data: ExtractedData) -> None:
        self._domain_event_publisher.publish(
            self.AGGREGATE_TYPE,
            str(extracted_data.document_id),
            extracted_data.events,
        )
