import pytest
from deps_extracted_data.model.extracted_data.field_deleted import ExtractedFieldDeleted

from deps_extraction.domain.dtos import ExtractedDataFilterObject
from deps_extraction.domain.exceptions import (
    ExtractedDataNotFound,
    ExtractedFieldNotFound,
)


@pytest.fixture
def extracted_data_service(application, domain_event_publisher):
    return application.extracted_data()


def test_delete_extracted_fields__valid_fields__success(
    extracted_data_service, saved_extracted_data, domain_event_publisher
):
    target_codes = [saved_extracted_data.fields[0].field_code, saved_extracted_data.fields[1].field_code]
    doc_id = saved_extracted_data.document_id

    all_field_codes = {field.field_code for field in saved_extracted_data.fields}
    assert set(target_codes).issubset(all_field_codes)

    saved_extracted_data.events.clear()
    extracted_data_service.delete_extracted_fields(document_id=doc_id, field_codes=target_codes)

    remaining_field_codes = {field.field_code for field in saved_extracted_data.fields}
    assert not set(target_codes).intersection(remaining_field_codes)

    domain_event_publisher.publish.assert_called_once()
    publish_args = domain_event_publisher.publish.call_args[0]
    assert publish_args[0] == "ExtractedData"
    assert publish_args[1] == str(doc_id)
    published_events = publish_args[2]
    assert len(published_events) == len(target_codes)
    for code, actual_event in zip(target_codes, published_events, strict=True):
        assert actual_event == ExtractedFieldDeleted(
            document_id=doc_id,
            field_code=code,
            deleted_at=actual_event.deleted_at,
        )


def test_delete_extracted_fields__field_code_missing__no_error(extracted_data_service, saved_extracted_data):
    extracted_data_service.delete_extracted_fields(
        document_id=saved_extracted_data.document_id, field_codes=["nonexistent_code"]
    )


def test_delete_extracted_fields__document_missing__raises_not_found(extracted_data_service):
    with pytest.raises(ExtractedDataNotFound):
        extracted_data_service.delete_extracted_fields(document_id=999999, field_codes=["code1"])


def test_get_extracted_fields_by_filter__fields_exist__returns_matching(extracted_data_service, saved_extracted_data):
    target_code = saved_extracted_data.fields[0].field_code
    filtering = ExtractedDataFilterObject(document_id=saved_extracted_data.document_id, field_codes=[target_code])
    result = extracted_data_service.get_extracted_fields_by_filter(filtering)
    assert len(result) == 1
    assert result[0].field_code == target_code


def test_get_extracted_fields_by_filter__code_missing__raises_not_found(extracted_data_service, saved_extracted_data):
    filtering = ExtractedDataFilterObject(document_id=saved_extracted_data.document_id, field_codes=["nonexistent"])
    with pytest.raises(ExtractedFieldNotFound):
        extracted_data_service.get_extracted_fields_by_filter(filtering)


def test_get_extracted_fields_by_filter__document_missing__raises_not_found(extracted_data_service):
    filtering = ExtractedDataFilterObject(document_id=999999, field_codes=["code1"])
    with pytest.raises(ExtractedDataNotFound):
        extracted_data_service.get_extracted_fields_by_filter(filtering)
