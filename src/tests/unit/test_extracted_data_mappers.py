from deps_extraction.infrastructure.repositories.extracted_data.mappers import (
    ExtractedDataMapper,
)
from tests.data.extracted_data import full_extracted_data_without_optional_elements


def test_extracted_data_mapper():
    field = ExtractedDataMapper().from_dicts(full_extracted_data_without_optional_elements)
    res = ExtractedDataMapper().to_dicts(field)

    for el in full_extracted_data_without_optional_elements:
        el.pop("groups")
    assert res["fields"] == full_extracted_data_without_optional_elements
