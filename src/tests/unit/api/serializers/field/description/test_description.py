import pytest
from pydantic import ValidationError

from deps_extraction.api.serializers.document_type.profile.description import (
    SerializedDateDescription,
    SerializedDictDescription,
    SerializedEnumDescription,
    SerializedListDescription,
    SerializedStringDescription,
    SerializedTableDescription,
)
from tests.factories.document_type.profile import (
    DateFieldDescriptionFactory,
    DictFieldDescriptionFactory,
    EnumFieldDescriptionFactory,
    ListFieldDescriptionFactory,
    StringFieldDescriptionFactory,
    TableFieldDescriptionFactory,
)


@pytest.mark.document_type
def test_enum_description_field__ok():
    enum_description = EnumFieldDescriptionFactory()

    serialized_description = SerializedEnumDescription.from_model(enum_description)

    assert enum_description == serialized_description.to_model()


@pytest.mark.document_type
def test_date_description_field__ok():
    date_description = DateFieldDescriptionFactory()

    serialized_description = SerializedDateDescription.from_model(date_description)

    assert date_description == serialized_description.to_model()


@pytest.mark.document_type
def test_string_description_field__ok():
    string_description = StringFieldDescriptionFactory()

    serialized_description = SerializedStringDescription.from_model(string_description)

    assert string_description == serialized_description.to_model()


@pytest.mark.document_type
def test_dict_description_field__ok():
    dict_description = DictFieldDescriptionFactory()

    serialized_description = SerializedDictDescription.from_model(dict_description)

    assert dict_description == serialized_description.to_model()


@pytest.mark.document_type
def test_list_description_field__ok():
    list_description = ListFieldDescriptionFactory()

    serialized_description = SerializedListDescription.from_model(list_description)

    assert list_description == serialized_description.to_model()


@pytest.mark.document_type
def test_table_description_field__ok():
    table_description = TableFieldDescriptionFactory()

    serialized_description = SerializedTableDescription.from_model(table_description)

    assert table_description == serialized_description.to_model()


@pytest.mark.document_type
def test_list_description_field__invalid_base_type_meta__error():
    with pytest.raises(ValidationError):
        SerializedListDescription(
            baseType="dict",
            baseTypeMeta={},
        )
