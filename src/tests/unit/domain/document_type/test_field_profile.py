import pytest

from deps_extraction.domain.exceptions import InconsistentProfileDescription
from deps_extraction.domain.model import FieldProfile, FieldType
from tests.factories.document_type.profile import (
    DateFieldDescriptionFactory,
    DictFieldDescriptionFactory,
    EnumFieldDescriptionFactory,
    ListFieldDescriptionFactory,
    StringFieldDescriptionFactory,
    TableFieldDescriptionFactory,
)


def test_default_profile_validation__empty_desc__no_error():
    FieldProfile(FieldType.STRING, None)


def test_default_profile_validation__string_with_string__no_error():
    FieldProfile(FieldType.STRING, StringFieldDescriptionFactory())


@pytest.mark.parametrize(
    "description_factory",
    (
        DictFieldDescriptionFactory,
        TableFieldDescriptionFactory,
        ListFieldDescriptionFactory,
        EnumFieldDescriptionFactory,
        DateFieldDescriptionFactory,
    ),
)
def test_default_profile_validation__invalid__error(description_factory):
    with pytest.raises(InconsistentProfileDescription):
        FieldProfile(FieldType.STRING, description_factory())


@pytest.mark.parametrize(
    "description_factory,valid_type",
    (
        (DictFieldDescriptionFactory, FieldType.DICT),
        (TableFieldDescriptionFactory, FieldType.TABLE),
        (ListFieldDescriptionFactory, FieldType.LIST),
        (EnumFieldDescriptionFactory, FieldType.ENUM),
        (DateFieldDescriptionFactory, FieldType.DATE),
    ),
)
def test_default_profile_validation__valid__no_error(description_factory, valid_type):
    FieldProfile(valid_type, description_factory())
