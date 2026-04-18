import pytest

from deps_extraction.domain.model import DocumentType, ExtractorType
from deps_extraction.infrastructure.repositories import DocumentTypeRepository
from tests.data import create_field_payload, create_field_payload_2


@pytest.mark.document_type
def test_move_fields_between_extractors__happy_path(
    fake_document_type_repository: DocumentTypeRepository,
    extractor_factory,
    document_type_factory,
    test_document_type: DocumentType,
):
    source_extractor = extractor_factory(fields_size=0, type_=ExtractorType.PLUGIN)
    target_extractor = extractor_factory(fields_size=0, type_=ExtractorType.PLUGIN)

    fields = [
        source_extractor.add_field(
            name=create_field_payload["name"],
            type_=create_field_payload["type"],
            required=create_field_payload["required"],
            confidential=True,
            read_only=False,
        ),
        source_extractor.add_field(
            name=create_field_payload_2["name"],
            type_=create_field_payload_2["type"],
            required=create_field_payload_2["required"],
            confidential=True,
            read_only=False,
        ),
    ]

    fake_document_type_repository.save(test_document_type)

    document_type = document_type_factory(
        id_=test_document_type.id,
        tenant_id=test_document_type.tenant_id,
        extractors={
            source_extractor.id(): source_extractor,
            target_extractor.id(): target_extractor,
        },
    )

    moved_codes = [field.code.value for field in fields]

    document_type.move_fields_between_extractors(
        source_extractor_id=source_extractor.id(),
        target_extractor_id=target_extractor.id(),
        fields_codes=moved_codes,
    )

    assert all(target_extractor.field_storage.get(code) is not None for code in moved_codes)
