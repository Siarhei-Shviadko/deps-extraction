import pytest

from deps_extraction.domain.exceptions import (
    FieldAlreadyExistsError,
    FieldNotFound,
    InvariantViolation,
)
from deps_extraction.domain.model import Extractor, ExtractorType
from tests.data import create_field_payload, create_field_payload_2


def test_extractor__ok(extractor_factory):
    extractor = extractor_factory()

    assert extractor


def test_extractor__add_field__ok(extractor_factory):
    extractor = extractor_factory(fields_size=0, type_=ExtractorType.PLUGIN)
    field = extractor.add_field(
        name=create_field_payload["name"], type_=create_field_payload["type"], required=create_field_payload["required"]
    )

    assert field in extractor.fields
    assert field.name == create_field_payload["name"]
    assert field.profile.type == create_field_payload["type"]
    assert field.required == create_field_payload["required"]


def test_extractor__add_field_with_code__ok(extractor_factory):
    extractor = extractor_factory(fields_size=0, type_=ExtractorType.PLUGIN)
    code = "TestCode"
    field = extractor.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
        code=code,
    )

    assert field in extractor.fields
    assert field.name == create_field_payload["name"]
    assert field.profile.type == create_field_payload["type"]
    assert field.required == create_field_payload["required"]
    assert field.code() == code


def test_extractor__add_field__code_exists__error(extractor_factory):
    extractor = extractor_factory(fields_size=0, type_=ExtractorType.PLUGIN)
    field = extractor.add_field(
        name=create_field_payload["name"], type_=create_field_payload["type"], required=create_field_payload["required"]
    )

    with pytest.raises(FieldAlreadyExistsError):
        extractor.add_field(
            name=create_field_payload["name"],
            type_=create_field_payload["type"],
            required=create_field_payload["required"],
            code=field.code(),
        )


def test_extractor__add_field__name_exists__error(extractor_factory):
    extractor = extractor_factory(fields_size=0, type_=ExtractorType.PLUGIN)
    field = extractor.add_field(
        name=create_field_payload["name"], type_=create_field_payload["type"], required=create_field_payload["required"]
    )

    with pytest.raises(InvariantViolation) as err:
        extractor.add_field(
            name=create_field_payload["name"],
            type_=create_field_payload["type"],
            required=create_field_payload["required"],
        )

    error_message = err.value.args[0]
    assert f"Field with name `{field.name}` already exists!" == error_message


def test_extractor__add_field_for_llm_extractor__ok(extractor_factory):
    extractor = extractor_factory(fields_size=0, type_=ExtractorType.LLM)
    field = extractor.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
    )

    assert extractor.field_storage[field.code()]
    assert extractor.field_storage[field.code()].name == create_field_payload["name"]
    assert extractor.field_storage[field.code()].profile.type == create_field_payload["type"]
    assert extractor.field_storage[field.code()].required == create_field_payload["required"]


def test_extractor__add_field__compliance_policy_added(extractor_factory):
    extractor = extractor_factory(fields_size=0, type_=ExtractorType.PLUGIN)
    field = extractor.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
        confidential=True,
        read_only=False,
    )

    assert len(extractor.compliance_policies) == 1
    assert extractor.compliance_policies[0].code == field.code


def test_extractor__update_field__updated(extractor_factory):
    extractor: Extractor = extractor_factory(fields_size=0, type_=ExtractorType.PLUGIN)
    field = extractor.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
        confidential=False,
        read_only=False,
    )
    expected_name = "changed_name"
    expected_order = 101
    updated_field = extractor.update_field(
        code=field.code(),
        name=expected_name,
        required=not create_field_payload["required"],
        confidential=True,
        read_only=True,
        order=expected_order,
    )

    assert updated_field.name == expected_name
    assert updated_field.required == bool(not create_field_payload["required"])
    assert extractor.compliance_storage[field.code()].confidential is True
    assert extractor.compliance_storage[field.code()].read_only is True
    assert updated_field.display_order == expected_order


def test_extractor__not_unique_name__error(extractor_factory):
    extractor: Extractor = extractor_factory(fields_size=2, type_=ExtractorType.PLUGIN)

    first_name = extractor.fields[0].name
    second_field_code = extractor.fields[1].code()

    with pytest.raises(InvariantViolation):
        extractor.update_field(code=second_field_code, name=first_name)


def test_extractor__same_name_for_field__no_error(extractor_factory):
    extractor: Extractor = extractor_factory(fields_size=2, type_=ExtractorType.PLUGIN)

    first_name = extractor.fields[0].name
    first_field_code = extractor.fields[0].code()

    extractor.update_field(code=first_field_code, name=first_name)


def test_extractor__wrong_code__error(extractor_factory):
    extractor: Extractor = extractor_factory(fields_size=2, type_=ExtractorType.PLUGIN)

    with pytest.raises(FieldNotFound):
        extractor.update_field(code="fake_code", name="updated")


def test_extractor__update__ok(extractor_factory):
    extractor: Extractor = extractor_factory(fields_size=0, type_=ExtractorType.LLM)
    field = extractor.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
    )

    expected_name = "Changed name"
    extractor.update_field(code=field.code(), name=expected_name)

    assert extractor.field_storage[field.code()].name == expected_name


def test_extractor_delete_field__ok(extractor_factory):
    extractor: Extractor = extractor_factory(fields_size=0, type_=ExtractorType.PLUGIN)
    field1 = extractor.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
    )
    field2 = extractor.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
    )

    assert len(extractor.fields) == 2
    assert len(extractor.compliance_policies) == 2

    extractor.delete_field(field1.code())

    assert len(extractor.fields) == 1
    assert len(extractor.compliance_policies) == 1
    assert extractor.compliance_policies[0].code() == field2.code()
    assert extractor.fields[0].code() == field2.code()


def test_extractor_delete_field__wrong_code__no_errors(extractor_factory):
    extractor: Extractor = extractor_factory(fields_size=0, type_=ExtractorType.LLM)
    extractor.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
    )

    extractor.delete_field("fake_code")


def test_extractor_delete_field__no_fields__no_errors(extractor_factory):
    extractor: Extractor = extractor_factory(fields_size=0, type_=ExtractorType.LLM)

    extractor.delete_field("fake_code")
