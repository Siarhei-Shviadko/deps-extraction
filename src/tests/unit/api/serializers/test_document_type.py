import pytest

from deps_extraction.api.serializers import SerializedDocumentType
from deps_extraction.domain.model import ExtractionType


@pytest.mark.document_type
@pytest.mark.parametrize(
    "fixture", ["test_document_type_plugin_extractor_with_field", "test_document_type_llm_extractor_with_field"]
)
def test_serialized_document_type__ok(request, fixture):
    document_type = request.getfixturevalue(fixture)

    serialized_document_type = SerializedDocumentType.from_model(document_type)

    extraction_type = None if document_type.extraction_type == ExtractionType.NON else document_type.extraction_type

    assert serialized_document_type.id == document_type.id()
    assert serialized_document_type.document_type == document_type.name
    assert serialized_document_type.tenant_id == document_type.tenant_id()
    assert serialized_document_type.extraction_type == extraction_type
