import pytest

from deps_extraction.api.serializers import SerializedField

FIRST_ELEMENT = 0


@pytest.mark.document_type
def test_serialized_field__ok(test_document_type_llm_extractor_with_field):
    field = test_document_type_llm_extractor_with_field.composite_fields[FIRST_ELEMENT]

    serialized_field = SerializedField.from_model(test_document_type_llm_extractor_with_field.id(), field)

    assert serialized_field.name == field.name
    assert serialized_field.code == field.code()
    assert serialized_field.field_type == field.profile.type
    assert serialized_field.required == field.required


@pytest.mark.document_type
def test_serialized_extraction_field__from_model__ok(test_document_type_llm_extractor_with_field):
    field = test_document_type_llm_extractor_with_field.composite_fields[FIRST_ELEMENT]

    serialized_extraction_field = SerializedField.from_model(test_document_type_llm_extractor_with_field.id(), field)

    assert serialized_extraction_field.code == field.code()
    assert serialized_extraction_field.name == field.name
    assert serialized_extraction_field.field_type == field.profile.type
    assert serialized_extraction_field.required == field.required
    assert serialized_extraction_field.confidential == field.confidential
    assert serialized_extraction_field.read_only == field.read_only

    raw_serialized_extraction_field = serialized_extraction_field.dict(by_alias=True)

    assert raw_serialized_extraction_field["code"] == field.code()
    assert raw_serialized_extraction_field["name"] == field.name
    assert raw_serialized_extraction_field["fieldType"] == field.profile.type
    assert raw_serialized_extraction_field["required"] == field.required
    assert raw_serialized_extraction_field["confidential"] == field.confidential
    assert raw_serialized_extraction_field["readOnly"] == field.read_only
