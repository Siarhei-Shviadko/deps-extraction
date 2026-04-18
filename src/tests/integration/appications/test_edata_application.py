import pytest

from deps_extraction.domain.exceptions import ExtractedFieldUpdateAliasesError


def test_update_aliases__invalid_data__error(extracted_data_service, saved_extacted_data_with_with_aliases):
    aliases = {"fake_element_id": "alias"}

    with pytest.raises(ExtractedFieldUpdateAliasesError):
        extracted_data_service.update_aliases(
            document_id=saved_extacted_data_with_with_aliases.document_id,
            field_code=saved_extacted_data_with_with_aliases.fields[0].field_code,
            aliases=aliases,
        )
