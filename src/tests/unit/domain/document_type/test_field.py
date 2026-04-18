import uuid

import pytest

from deps_extraction.domain.exceptions import IllegalArgument
from deps_extraction.domain.model import ExtractionField
from tests.factories import ExtractionFieldFactory


@pytest.mark.document_type
def test_repr(test_field: ExtractionField) -> None:
    assert repr(test_field)


@pytest.mark.document_type
def test_create_updated(test_field: ExtractionField) -> None:
    new_name = uuid.uuid4().hex
    new_required = not test_field.required

    updated_field = test_field.create_updated(name=new_name, required=new_required)

    assert updated_field is not test_field
    assert updated_field.name == new_name
    assert updated_field.required == new_required
    assert updated_field.code == test_field.code
    assert updated_field.profile.type == test_field.profile.type


@pytest.mark.document_type
@pytest.mark.parametrize(
    "name,is_valid",
    (
        ("1", True),
        ("en", True),
        ("бе", True),
        ("这份文件的标题是中文", True),
        ("Words with spaces", True),
        ("abc @ : \" ' = a", True),
        ("1234", True),
        ("snake_case", True),
        ("Words-with-dashes", True),
        ("Words-with-dashes and spaces", True),
        ("", False),
        (" ", False),
        ("trailing space ", False),
        (" starting space", False),
        ("multi  spaces", False),
    ),
)
def test_create__name_checked(name, is_valid):
    if is_valid:
        assert ExtractionFieldFactory(name=name).name == name
    else:
        with pytest.raises(IllegalArgument):
            ExtractionFieldFactory(name=name)
