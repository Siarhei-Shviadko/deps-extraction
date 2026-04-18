import pytest

from deps_extraction.domain.dtos import ExtractedDataFilterObject
from deps_extraction.domain.exceptions import (
    ExtractedDataNotFound,
    ExtractedFieldNotFound,
)


def test_get_extracted_fields_by_filter__fields_exist__returns_matching_fields(
    extracted_data_service, saved_extracted_data
):
    target_codes = [saved_extracted_data.fields[0].field_code, saved_extracted_data.fields[1].field_code]
    filtering = ExtractedDataFilterObject(document_id=saved_extracted_data.document_id, field_codes=target_codes)

    result = extracted_data_service.get_extracted_fields_by_filter(filtering)

    assert len(result) == 2
    returned_codes = {f.field_code for f in result}
    assert returned_codes == set(target_codes)


def test_get_extracted_fields_by_filter__document_missing__raises_not_found(
    extracted_data_service,
):
    filtering = ExtractedDataFilterObject(document_id=999999, field_codes=["code1"])

    with pytest.raises(ExtractedDataNotFound):
        extracted_data_service.get_extracted_fields_by_filter(filtering)


def test_get_extracted_fields_by_filter__field_code_missing__raises_not_found(
    extracted_data_service, saved_extracted_data
):
    filtering = ExtractedDataFilterObject(
        document_id=saved_extracted_data.document_id,
        field_codes=[saved_extracted_data.fields[0].field_code, "nonexistent_code"],
    )

    with pytest.raises(ExtractedFieldNotFound):
        extracted_data_service.get_extracted_fields_by_filter(filtering)
