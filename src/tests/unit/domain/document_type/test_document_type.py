import uuid

import pytest

from deps_extraction.domain.events import (
    ExtractorAttached,
    ExtractorDetached,
    ExtractorFieldCreated,
    ExtractorFieldDeleted,
    ExtractorFieldUpdated,
)
from deps_extraction.domain.exceptions import (
    AttachmentExtractorConflict,
    ExtractionWorkflowCreationError,
    ExtractorNotFound,
    FieldAlreadyExistsError,
    IllegalArgument,
    InvariantViolation,
)
from deps_extraction.domain.model import (
    DocumentType,
    DocumentTypeFactory,
    ExtractionType,
    ExtractorType,
    FieldAttachment,
    FieldType,
    StringFieldDescription,
)
from tests.data import (
    create_field_payload,
    create_field_payload_2,
    create_field_with_full_payload,
    raw_plugin_document_type,
    raw_prototype_document_type,
    raw_template_document_type,
    update_field_payload,
)

empty_list: list = []
FIRST_ELEMENT: int = 0


def _get_extractor_id(document_type: DocumentType, index: int) -> str:
    return list(document_type.extractors.keys())[index]


@pytest.mark.document_type
def test_factory__created(raw_document_type):
    document_type = DocumentTypeFactory.create(
        tenant_id=raw_document_type["tenant_id"],
        name=raw_document_type["name"],
        id_=raw_document_type["document_type_id"],
        extraction_type=raw_document_type["extraction_type"],
    )

    extraction_type = document_type.extraction_type.value if document_type.extraction_type else ExtractionType.NON

    assert document_type.id() == raw_document_type["document_type_id"]
    assert document_type.tenant_id() == raw_document_type["tenant_id"]
    assert document_type.name == raw_document_type["name"]
    assert document_type.extraction_fields == empty_list
    assert document_type.compliance_policies == empty_list

    if raw_document_type["extraction_type"] is None:
        assert extraction_type == ExtractionType.NON
    else:
        assert extraction_type == raw_document_type["extraction_type"]


@pytest.mark.document_type
@pytest.mark.parametrize(
    "raw_document_type", (raw_plugin_document_type, raw_prototype_document_type, raw_template_document_type)
)
def test_factory__with__fields__created(raw_document_type):
    document_type = DocumentTypeFactory.create(
        tenant_id=raw_document_type["tenant_id"],
        name=raw_document_type["name"],
        id_=raw_document_type["document_type_id"],
        extraction_type=raw_document_type["extraction_type"],
        fields=raw_document_type["fields"],
    )

    assert document_type.id() == raw_document_type["document_type_id"]
    assert document_type.tenant_id() == raw_document_type["tenant_id"]
    assert document_type.name == raw_document_type["name"]
    assert len(document_type.extraction_fields) == len(raw_document_type["fields"])
    assert len(document_type.compliance_policies) == len(raw_document_type["fields"])

    assert document_type.extraction_type.value == raw_document_type["extraction_type"]


@pytest.mark.document_type
def test_command_channel(test_document_type):
    assert test_document_type.command_channel == f"{test_document_type.name}-{test_document_type.tenant_id()}"


@pytest.mark.document_type
def test_repr(test_document_type):
    assert repr(test_document_type)


def test_attach_llm_extractor__ok(test_document_type):
    assert len(test_document_type.extractors) == 0

    extractor = test_document_type.attach_extractor(type_=ExtractorType.LLM, fields=[])

    assert len(test_document_type.extractors) == 1
    assert test_document_type.extractors[extractor.id()].type == ExtractorType.LLM
    assert test_document_type.extractors[extractor.id()].fields == []


def test_attach_llm_extractor__with_existing_id_and_different_type__error(test_document_type):
    assert len(test_document_type.extractors) == 0

    extractor = test_document_type.attach_extractor(type_=ExtractorType.LLM, fields=[])

    assert len(test_document_type.extractors) == 1
    assert test_document_type.extractors[extractor.id()].type == ExtractorType.LLM
    assert test_document_type.extractors[extractor.id()].fields == []
    with pytest.raises(AttachmentExtractorConflict):
        test_document_type.attach_extractor(extractor_id=extractor.id(), type_=ExtractorType.TEMPLATE, fields=[])


def test_attach_plugin_extractor__ok(test_document_type):
    assert len(test_document_type.extractors) == 0
    assert test_document_type.extraction_type == ExtractionType.NON

    extractor = test_document_type.attach_extractor(type_=ExtractorType.PLUGIN, fields=[])

    assert len(test_document_type.extractors) == 1
    assert test_document_type.extractors[extractor.id()].type == ExtractorType.PLUGIN
    assert test_document_type.extractors[extractor.id()].fields == []


def test_attach_second_llm_extractor_to_llm_extractor__ok(test_document_type):
    assert len(test_document_type.extractors) == 0

    extractor1 = test_document_type.attach_extractor(type_=ExtractorType.LLM, fields=[])
    extractor2 = test_document_type.attach_extractor(type_=ExtractorType.LLM, fields=[])

    assert len(test_document_type.extractors) == 2
    assert test_document_type.extractors[extractor1.id()].type == ExtractorType.LLM
    assert test_document_type.extractors[extractor2.id()].type == ExtractorType.LLM
    assert test_document_type.extractors[extractor1.id()].fields == []
    assert test_document_type.extractors[extractor2.id()].fields == []


def test_attach_second_llm_extractor_to_plugin_extractor__ok(test_document_type):
    assert len(test_document_type.extractors) == 0

    plugin_extractor = test_document_type.attach_extractor(type_=ExtractorType.PLUGIN, fields=[])
    llm_extractor = test_document_type.attach_extractor(type_=ExtractorType.LLM, fields=[])

    assert len(test_document_type.extractors) == 2
    assert test_document_type.extractors[plugin_extractor.id()].type == ExtractorType.PLUGIN
    assert test_document_type.extractors[llm_extractor.id()].type == ExtractorType.LLM
    assert test_document_type.extractors[plugin_extractor.id()].fields == []
    assert test_document_type.extractors[llm_extractor.id()].fields == []


def test_attach_plugin_to_llm_extractor__ok(test_document_type):
    assert len(test_document_type.extractors) == 0

    llm_extractor = test_document_type.attach_extractor(type_=ExtractorType.LLM, fields=[])
    plugin_extractor = test_document_type.attach_extractor(type_=ExtractorType.PLUGIN, fields=[])

    assert len(test_document_type.extractors) == 2
    assert test_document_type.extractors[llm_extractor.id()].type == ExtractorType.LLM
    assert test_document_type.extractors[plugin_extractor.id()].type == ExtractorType.PLUGIN
    assert test_document_type.extractors[llm_extractor.id()].fields == []
    assert test_document_type.extractors[plugin_extractor.id()].fields == []


def test_attach_plugin_second_time__no_changes(test_document_type):
    assert len(test_document_type.extractors) == 0

    extractor1 = test_document_type.attach_extractor(type_=ExtractorType.PLUGIN, fields=[])
    extractor2 = test_document_type.attach_extractor(type_=ExtractorType.PLUGIN, fields=[])

    assert len(test_document_type.extractors) == 1
    assert extractor1 == extractor2
    assert test_document_type.extractors[extractor1.id()].type == ExtractorType.PLUGIN
    assert test_document_type.extractors[extractor1.id()].fields == []


def test_attach_extractor___extractor_id_provided__extractor_updated(test_document_type, attach_extractor_fields_2):
    assert len(test_document_type.extractors) == 0

    extractor = test_document_type.attach_extractor(type_=ExtractorType.LLM, fields=[])

    test_document_type.attach_extractor(
        type_=ExtractorType.LLM, fields=attach_extractor_fields_2, extractor_id=extractor.id()
    )

    assert len(test_document_type.extractors) == 1
    assert test_document_type.extractors[extractor.id()].type == ExtractorType.LLM
    assert len(test_document_type.extractors[extractor.id()].fields) == len(attach_extractor_fields_2)


@pytest.mark.document_type
def test_create_field__created__default_compliance(test_document_type_with_llm_extractors: DocumentType):
    assert not test_document_type_with_llm_extractors.extraction_fields
    first_extractor_id = _get_extractor_id(test_document_type_with_llm_extractors, FIRST_ELEMENT)
    field = test_document_type_with_llm_extractors.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
        extractor_id=first_extractor_id,
    )

    assert field.code
    assert field.name == create_field_payload["name"]
    assert field.required == create_field_payload["required"]

    compliance = test_document_type_with_llm_extractors.extractors[first_extractor_id].compliance_policies[
        FIRST_ELEMENT
    ]
    assert compliance.code == field.code
    assert compliance.confidential is False
    assert compliance.read_only is False

    expected_extractor_type = (
        test_document_type_with_llm_extractors.extractors[first_extractor_id].type
        if test_document_type_with_llm_extractors.extractors[first_extractor_id].type != ExtractorType.LLM
        else ExtractionType.NON
    )
    expected_event = ExtractorFieldCreated(
        code=field.code(),
        name=field.name,
        document_type_code=test_document_type_with_llm_extractors.id(),
        extractor_id=test_document_type_with_llm_extractors.extractors[first_extractor_id].id(),
        extractor_type=expected_extractor_type.value,
        field_type=field.profile.type,
        required=field.required,
        order=field.display_order,
        confidential=field.confidential,
        read_only=field.read_only,
        description=field.profile.description,
    )

    actual_events = test_document_type_with_llm_extractors.events
    assert expected_event in actual_events


@pytest.mark.document_type
def test_add_field__created(test_document_type_with_llm_extractors: DocumentType):
    assert not test_document_type_with_llm_extractors.extraction_fields
    first_extractor_id = _get_extractor_id(test_document_type_with_llm_extractors, FIRST_ELEMENT)
    field = test_document_type_with_llm_extractors.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
        extractor_id=first_extractor_id,
    )

    assert field.code
    assert field.name == create_field_payload_2["name"]
    assert field.profile.type == create_field_payload_2["type"]
    assert field.required == create_field_payload_2["required"]

    expected_extractor_type = (
        test_document_type_with_llm_extractors.extractors[first_extractor_id].type
        if test_document_type_with_llm_extractors.extractors[first_extractor_id].type != ExtractorType.LLM
        else ExtractionType.NON
    )

    expected_event = ExtractorFieldCreated(
        code=field.code(),
        name=field.name,
        document_type_code=test_document_type_with_llm_extractors.id(),
        extractor_id=test_document_type_with_llm_extractors.extractors[first_extractor_id].id(),
        extractor_type=expected_extractor_type.value,
        field_type=field.profile.type,
        required=field.required,
        order=field.display_order,
        confidential=field.confidential,
        read_only=field.read_only,
        description=field.profile.description,
    )
    actual_events = test_document_type_with_llm_extractors.events
    assert expected_event in actual_events


@pytest.mark.document_type
def test_add_field__no_llm_extractors__created(test_document_type_with_plugin_extractor: DocumentType):
    assert not [
        extractor
        for extractor in test_document_type_with_plugin_extractor.extractors.values()
        if extractor.type == ExtractorType.LLM
    ]
    field = test_document_type_with_plugin_extractor.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
    )

    assert field.code
    assert field.name == create_field_payload_2["name"]
    assert field.profile.type == create_field_payload_2["type"]
    assert field.required == create_field_payload_2["required"]

    latest_extractor_id = _get_extractor_id(test_document_type_with_plugin_extractor, -1)
    expected_extractor_type1 = (
        test_document_type_with_plugin_extractor.extractors[latest_extractor_id].type
        if test_document_type_with_plugin_extractor.extractors[latest_extractor_id].type != ExtractorType.LLM
        else ExtractionType.NON
    )
    expected_event1 = ExtractorFieldCreated(
        code=field.code(),
        name=field.name,
        document_type_code=test_document_type_with_plugin_extractor.id(),
        extractor_id=test_document_type_with_plugin_extractor.extractors[latest_extractor_id].id(),
        extractor_type=expected_extractor_type1.value,
        field_type=field.profile.type,
        required=field.required,
        order=field.display_order,
        confidential=field.confidential,
        read_only=field.read_only,
        description=field.profile.description,
    )

    actual_events = test_document_type_with_plugin_extractor.events

    assert expected_event1 in actual_events


def test_add_field_with_not_unique_name__error(test_document_type_with_llm_extractors: DocumentType):
    extractor_id = _get_extractor_id(test_document_type_with_llm_extractors, FIRST_ELEMENT)
    test_document_type_with_llm_extractors.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
        extractor_id=extractor_id,
    )

    with pytest.raises(InvariantViolation):
        test_document_type_with_llm_extractors.add_field(
            name=create_field_payload_2["name"],
            type_=create_field_payload_2["type"],
            required=create_field_payload_2["required"],
            extractor_id=extractor_id,
        )


def test_add_field_with_not_unique_name__doc_type_has_2_extractors__error(
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    first_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, FIRST_ELEMENT)
    second_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, 1)
    test_document_type_with_llm_and_plugin_extractors.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
        extractor_id=first_extractor_id,
    )

    with pytest.raises(InvariantViolation):
        test_document_type_with_llm_and_plugin_extractors.add_field(
            name=create_field_payload_2["name"],
            type_=create_field_payload_2["type"],
            required=create_field_payload_2["required"],
            extractor_id=second_extractor_id,
        )


def test_add_field_with_not_unique_code__doc_type_has_2_extractors__error(
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    first_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, FIRST_ELEMENT)
    second_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, 1)
    code = "TestCode"

    test_document_type_with_llm_and_plugin_extractors.add_field(
        code=code,
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
        extractor_id=first_extractor_id,
    )

    with pytest.raises(FieldAlreadyExistsError):
        test_document_type_with_llm_and_plugin_extractors.add_field(
            code=code,
            name=create_field_with_full_payload["name"],
            type_=create_field_with_full_payload["type_"],
            required=create_field_with_full_payload["required"],
            extractor_id=second_extractor_id,
        )


def test_add_fields__doc_type_has_2_extractors__field_for_plugin_added_added_without_extractor_id(
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    llm_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, FIRST_ELEMENT)
    field_1 = test_document_type_with_llm_and_plugin_extractors.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
        extractor_id=llm_extractor_id,
    )

    field_2 = test_document_type_with_llm_and_plugin_extractors.add_field(
        name=create_field_with_full_payload["name"],
        type_=create_field_with_full_payload["type_"],
        required=create_field_with_full_payload["required"],
    )

    llm_extractor = test_document_type_with_llm_and_plugin_extractors.extractors[
        _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, 0)
    ]
    plugin_extractor = test_document_type_with_llm_and_plugin_extractors.extractors[
        _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, 1)
    ]

    assert llm_extractor.type == ExtractorType.LLM
    assert plugin_extractor.type == ExtractorType.PLUGIN
    assert len(llm_extractor.fields) == 1
    assert len(plugin_extractor.fields) == 1
    assert len(test_document_type_with_llm_and_plugin_extractors.extraction_fields) == 2
    assert llm_extractor.fields[0].code == field_1.code
    assert plugin_extractor.fields[0].code == field_2.code


def test_add_field_for_plugin_extractor__extractor_id_not_provided__added(
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    field = test_document_type_with_llm_and_plugin_extractors.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
    )

    plugin_extractor = next(
        (
            e
            for e in test_document_type_with_llm_and_plugin_extractors.extractors.values()
            if e.type == ExtractorType.PLUGIN
        )
    )

    assert len(plugin_extractor.fields) == 1
    assert len(test_document_type_with_llm_and_plugin_extractors.extraction_fields) == 1
    assert field.name == create_field_payload_2["name"]


def test_add_field_for_llm_extractor__extractor_id_not_provided__error(
    test_document_type_with_llm_extractors: DocumentType,  # take doc type
):
    with pytest.raises(ExtractorNotFound):
        test_document_type_with_llm_extractors.add_field(
            name=create_field_payload_2["name"],
            type_=create_field_payload_2["type"],
            required=create_field_payload_2["required"],
        )


def test_add_field__doc_type_with_multiple_llm_extractors__added_to_plugin_extractor(
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    extractor1 = test_document_type_with_llm_and_plugin_extractors.attach_extractor(type_=ExtractorType.LLM, fields=[])
    extractor2 = test_document_type_with_llm_and_plugin_extractors.attach_extractor(type_=ExtractorType.LLM, fields=[])

    field = test_document_type_with_llm_and_plugin_extractors.add_field(
        name=create_field_with_full_payload["name"],
        type_=create_field_with_full_payload["type_"],
        required=create_field_with_full_payload["required"],
    )
    plugin_extractor = next(
        (
            extractor
            for extractor in test_document_type_with_llm_and_plugin_extractors.extractors.values()
            if extractor.type == ExtractorType.PLUGIN
        )
    )
    assert plugin_extractor.type == ExtractorType.PLUGIN
    assert len(plugin_extractor.fields) == 1
    assert len(test_document_type_with_llm_and_plugin_extractors.extraction_fields) == 1
    assert field.name == create_field_with_full_payload["name"]


def test_add_field__using_extractor_id__doc_type_with_multiple_llm_extractors__added_extractor(
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    extractor1 = test_document_type_with_llm_and_plugin_extractors.attach_extractor(
        type_=ExtractorType.LLM,
        fields=[],
    )
    extractor2 = test_document_type_with_llm_and_plugin_extractors.attach_extractor(
        type_=ExtractorType.LLM,
        fields=[],
    )
    extractor3 = test_document_type_with_llm_and_plugin_extractors.attach_extractor(
        type_=ExtractorType.LLM,
        fields=[],
    )

    field = test_document_type_with_llm_and_plugin_extractors.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
        extractor_id=extractor2.id(),
    )

    assert len(extractor2.fields) == 1
    assert len(test_document_type_with_llm_and_plugin_extractors.extraction_fields) == 1
    assert field.name == create_field_payload_2["name"]


def test_add_field__using_extractor_id__no_extractor_with_this_id__error(
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    with pytest.raises(ExtractorNotFound):
        test_document_type_with_llm_and_plugin_extractors.add_field(
            name=create_field_payload_2["name"],
            type_=create_field_payload_2["type"],
            required=create_field_payload_2["required"],
            extractor_id="FakeName",
        )


def test_add_field__no_extractor_for_this_field__error(
    test_document_type_with_llm_extractors: DocumentType,
):
    with pytest.raises(ExtractorNotFound):
        test_document_type_with_llm_extractors.add_field(
            name=create_field_payload_2["name"],
            type_=create_field_payload_2["type"],
            required=create_field_payload_2["required"],
        )


@pytest.mark.document_type
def test_update_field__field_exists__updated_event_added(
    test_document_type_plugin_extractor_with_field: DocumentType,
    test_field,
):
    compliance = test_document_type_plugin_extractor_with_field.compliance_policies[FIRST_ELEMENT]
    assert compliance.confidential is False
    assert compliance.read_only is False

    update_field_payload["code"] = test_field.code()
    new_confidential, new_read_only, updated_required = True, True, True
    updated_name = "another-name"

    test_document_type_plugin_extractor_with_field.update_field(
        code=update_field_payload["code"],
        name=updated_name,
        required=updated_required,
        read_only=new_read_only,
        confidential=new_confidential,
    )

    updated_field = test_document_type_plugin_extractor_with_field.extraction_fields[FIRST_ELEMENT]
    assert updated_field.name == updated_name
    assert updated_field.required == updated_required

    compliance = test_document_type_plugin_extractor_with_field.compliance_policies[FIRST_ELEMENT]
    assert compliance.code == updated_field.code
    assert compliance.confidential is new_confidential
    assert compliance.read_only is new_read_only

    expected_event = ExtractorFieldUpdated(
        code=update_field_payload["code"],
        name=updated_name,
        document_type_code=test_document_type_plugin_extractor_with_field.id(),
        extractor_id=list(test_document_type_plugin_extractor_with_field.extractors.values())[FIRST_ELEMENT].id(),
        extractor_type=test_document_type_plugin_extractor_with_field.extraction_type,
        field_type=test_field.profile.type,
        required=updated_required,
        order=test_field.display_order,
        confidential=new_confidential,
        read_only=new_read_only,
        description=test_field.profile.description,
    )

    actual_events = test_document_type_plugin_extractor_with_field.events
    assert expected_event in actual_events


@pytest.mark.document_type
def test_update_field__not_unique_name__error(test_document_type_plugin_extractor_with_field: DocumentType):
    first_name, second_name = "first-name", "second-name"

    test_document_type_plugin_extractor_with_field.add_field(
        name=first_name,
        type_=FieldType.STRING,
        required=update_field_payload["required"],
    )
    test_document_type_plugin_extractor_with_field.add_field(
        code=update_field_payload["code"],
        name=second_name,
        type_=FieldType.STRING,
        required=update_field_payload["required"],
    )

    with pytest.raises(InvariantViolation):
        test_document_type_plugin_extractor_with_field.update_field(code=update_field_payload["code"], name=first_name)


@pytest.mark.document_type
def test_update_field__not_unique_name__multiple_extractors__error(
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    first_name, second_name = "first-name", "second-name"
    first_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, FIRST_ELEMENT)
    last_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, -1)

    test_document_type_with_llm_and_plugin_extractors.add_field(
        code=update_field_payload["code"],
        name=first_name,
        type_=FieldType.STRING,
        required=update_field_payload["required"],
        extractor_id=first_extractor_id,
    )

    test_document_type_with_llm_and_plugin_extractors.add_field(
        name=second_name,
        type_=FieldType.STRING,
        required=update_field_payload["required"],
        extractor_id=last_extractor_id,
    )
    assert len(test_document_type_with_llm_and_plugin_extractors.extractors[first_extractor_id].fields) == 1
    assert (
        test_document_type_with_llm_and_plugin_extractors.extractors[first_extractor_id].fields[FIRST_ELEMENT].code()
        == update_field_payload["code"]
    )
    assert len(test_document_type_with_llm_and_plugin_extractors.extractors[last_extractor_id].fields) == 1

    with pytest.raises(InvariantViolation):
        test_document_type_with_llm_and_plugin_extractors.update_field(
            code=update_field_payload["code"],
            name=second_name,
            extractor_id=first_extractor_id,
        )


@pytest.mark.document_type
def test_update_field__multiple_extractors__updated(test_document_type_with_llm_and_plugin_extractors: DocumentType):
    first_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, FIRST_ELEMENT)
    last_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, -1)

    field_1 = test_document_type_with_llm_and_plugin_extractors.add_field(
        name="first_name",
        type_=FieldType.STRING,
        required=update_field_payload["required"],
        extractor_id=first_extractor_id,
    )

    field_2 = test_document_type_with_llm_and_plugin_extractors.add_field(
        name="second_name",
        type_=FieldType.STRING,
        required=update_field_payload["required"],
        extractor_id=last_extractor_id,
    )

    test_document_type_with_llm_and_plugin_extractors.update_field(
        field_1.code(), name="updated_name_1", extractor_id=first_extractor_id
    )
    test_document_type_with_llm_and_plugin_extractors.update_field(
        field_2.code(), name="updated_name_2", extractor_id=last_extractor_id
    )

    assert (
        test_document_type_with_llm_and_plugin_extractors.extractors[first_extractor_id].fields[FIRST_ELEMENT].name
        == "updated_name_1"
    )
    assert (
        test_document_type_with_llm_and_plugin_extractors.extractors[last_extractor_id].fields[FIRST_ELEMENT].name
        == "updated_name_2"
    )


@pytest.mark.document_type
def test_update_field__empty_payload__no_error(test_document_type_plugin_extractor_with_field: DocumentType):
    extractor = test_document_type_plugin_extractor_with_field.extractors[
        _get_extractor_id(test_document_type_plugin_extractor_with_field, FIRST_ELEMENT)
    ]
    test_field = extractor.fields[FIRST_ELEMENT]
    test_document_type_plugin_extractor_with_field.update_field(code=test_field.code())

    expected_event = ExtractorFieldUpdated(
        code=test_field.code(),
        name=test_field.name,
        document_type_code=test_document_type_plugin_extractor_with_field.id(),
        extractor_id=extractor.id(),
        extractor_type=test_document_type_plugin_extractor_with_field.extraction_type,
        field_type=test_field.profile.type,
        required=test_field.required,
        order=test_field.display_order,
        confidential=extractor.compliance_storage[test_field.code()].confidential,
        read_only=extractor.compliance_storage[test_field.code()].read_only,
        description=test_field.profile.description,
    )

    actual_events = test_document_type_plugin_extractor_with_field.events
    assert expected_event in actual_events


@pytest.mark.document_type
def test_update_field__field_exists__updated(
    test_document_type_with_llm_and_plugin_extractors_with_fields: DocumentType,
):
    code = test_document_type_with_llm_and_plugin_extractors_with_fields.extraction_fields[FIRST_ELEMENT].code
    update_field_payload["code"] = code()

    updated_field = test_document_type_with_llm_and_plugin_extractors_with_fields.update_field(**update_field_payload)
    first_extractor_id = _get_extractor_id(test_document_type_with_llm_and_plugin_extractors_with_fields, FIRST_ELEMENT)

    assert updated_field.name == update_field_payload["name"]
    assert updated_field.required == update_field_payload["required"]

    expected_extractor_type = (
        test_document_type_with_llm_and_plugin_extractors_with_fields.extractors[first_extractor_id].type
        if test_document_type_with_llm_and_plugin_extractors_with_fields.extractors[first_extractor_id].type
        != ExtractorType.LLM
        else ExtractionType.NON
    )
    expected_event = ExtractorFieldUpdated(
        code=code(),
        name=updated_field.name,
        document_type_code=test_document_type_with_llm_and_plugin_extractors_with_fields.id(),
        extractor_id=test_document_type_with_llm_and_plugin_extractors_with_fields.extractors[first_extractor_id].id(),
        extractor_type=expected_extractor_type.value,
        field_type=updated_field.profile.type,
        required=updated_field.required,
        order=updated_field.display_order,
        confidential=updated_field.confidential,
        read_only=updated_field.read_only,
        description=updated_field.profile.description,
    )

    actual_events = test_document_type_with_llm_and_plugin_extractors_with_fields.events
    assert expected_event in actual_events


@pytest.mark.document_type
def test_update_field__no_field__error(test_document_type: DocumentType):
    update_field_payload["code"] = uuid.uuid4().hex

    with pytest.raises(ExtractorNotFound):
        test_document_type.update_field(
            code=update_field_payload["code"],
            name=update_field_payload["name"],
        )

    assert not test_document_type.events


def test_update_field__same_field_name_for_extractor__no_error(
    test_document_type_plugin_extractor_with_field: DocumentType,
):
    code = test_document_type_plugin_extractor_with_field.extraction_fields[FIRST_ELEMENT].code()
    name = test_document_type_plugin_extractor_with_field.extraction_fields[FIRST_ELEMENT].name

    updated_field = test_document_type_plugin_extractor_with_field.update_field(
        code=code,
        name=name,
    )
    first_extractor_id = _get_extractor_id(test_document_type_plugin_extractor_with_field, FIRST_ELEMENT)
    expected_extractor_type = (
        test_document_type_plugin_extractor_with_field.extractors[first_extractor_id].type
        if test_document_type_plugin_extractor_with_field.extractors[first_extractor_id].type != ExtractorType.LLM
        else ExtractionType.NON
    )
    expected_event = ExtractorFieldUpdated(
        code=updated_field.code(),
        name=updated_field.name,
        document_type_code=test_document_type_plugin_extractor_with_field.id(),
        extractor_id=test_document_type_plugin_extractor_with_field.extractors[first_extractor_id].id(),
        extractor_type=expected_extractor_type.value,
        field_type=updated_field.profile.type,
        required=updated_field.required,
        order=updated_field.display_order,
        confidential=updated_field.confidential,
        read_only=updated_field.read_only,
        description=updated_field.profile.description,
    )

    actual_events = test_document_type_plugin_extractor_with_field.events
    assert expected_event in actual_events


@pytest.mark.document_type
def test_delete_regular_field__field_exists__deleted(
    test_document_type_with_plugin_extractor: DocumentType, test_field
):
    assert test_document_type_with_plugin_extractor.extraction_fields
    assert test_document_type_with_plugin_extractor.compliance_policies

    test_document_type_with_plugin_extractor.delete_field(test_field.code())

    assert not test_document_type_with_plugin_extractor.extraction_fields
    assert not test_document_type_with_plugin_extractor.compliance_policies
    first_extractor_id = _get_extractor_id(test_document_type_with_plugin_extractor, FIRST_ELEMENT)
    expected_event = ExtractorFieldDeleted(
        code=test_field.code(),
        document_type_code=test_document_type_with_plugin_extractor.id(),
        extractor_id=test_document_type_with_plugin_extractor.extractors[first_extractor_id].id(),
        extractor_type=test_document_type_with_plugin_extractor.extraction_type,
    )

    assert expected_event in test_document_type_with_plugin_extractor.events


@pytest.mark.document_type
def test_delete_field__no_extractor__no_error(test_document_type: DocumentType):
    assert not test_document_type.extraction_fields

    test_document_type.delete_field(uuid.uuid4().hex)

    assert not test_document_type.events


@pytest.mark.document_type
def test_delete_field__wrong_code__no_error(
    test_document_type_with_llm_and_plugin_extractors_with_fields: DocumentType,
):
    assert test_document_type_with_llm_and_plugin_extractors_with_fields.extraction_fields

    test_document_type_with_llm_and_plugin_extractors_with_fields.delete_field(uuid.uuid4().hex)

    assert not test_document_type_with_llm_and_plugin_extractors_with_fields.events


@pytest.mark.document_type
def test_delete_field__no_fields__no_error(test_document_type: DocumentType):
    test_document_type.attach_extractor(ExtractorType.PROTOTYPE, fields=[])

    test_document_type.delete_field(uuid.uuid4().hex)

    assert len(test_document_type.events) == 1
    assert type(test_document_type.events[FIRST_ELEMENT]) != ExtractorFieldDeleted


@pytest.mark.document_type
def test_delete_field__with_extractor_id__ok(
    test_document_type_with_llm_and_plugin_extractors_with_fields: DocumentType,
):
    expected_extractor = test_document_type_with_llm_and_plugin_extractors_with_fields.extractors[
        _get_extractor_id(test_document_type_with_llm_and_plugin_extractors_with_fields, -1)
    ]
    field_for_delete = expected_extractor.fields[FIRST_ELEMENT]

    assert len(expected_extractor.fields) == 1

    test_document_type_with_llm_and_plugin_extractors_with_fields.delete_field(
        extractor_id=expected_extractor.id(), code=field_for_delete.code()
    )

    assert len(expected_extractor.fields) == 0
    assert field_for_delete.code() not in [
        field.code() for field in test_document_type_with_llm_and_plugin_extractors_with_fields.extraction_fields
    ]


@pytest.mark.parametrize(
    "name,is_valid",
    (
        ("1", True),
        ("en", True),
        ("бе", True),
        ("钟希娜", True),
        ("Words with spaces", True),
        ("1234", True),
        ("snake_case", True),
        ("Words-with-dashes", True),
        ("Words-with-dashes and spaces", True),
        ("", False),
        (" ", False),
        ("-", False),
        ("%%$@", False),
        ("trailing space ", False),
        ("- Dash-started", False),
        ("Dash ended -", False),
        ("Multiple  Spaces", False),
        ("A + B", False),
        ("🐍", False),
    ),
)
@pytest.mark.document_type
def test_create_name__expected_result(name, is_valid):
    if is_valid:
        assert DocumentTypeFactory.create(tenant_id=uuid.uuid4().hex, name=name).name == name
    else:
        with pytest.raises(IllegalArgument):
            DocumentTypeFactory.create(tenant_id=uuid.uuid4().hex, name=name)


@pytest.mark.document_type
def test_copy_fields_from__doc_type_from_template_to_template__copied(
    test_document_type_with_template_extractors: DocumentType,
):
    target_document_type = DocumentTypeFactory.create(
        tenant_id=uuid.uuid4().hex, name="target dt", extraction_type=ExtractionType.TEMPLATE
    )
    target_document_type.copy_fields_from(test_document_type_with_template_extractors)

    assert target_document_type.composite_fields == test_document_type_with_template_extractors.composite_fields
    assert len(target_document_type.extractors) == len(test_document_type_with_template_extractors.extractors)


@pytest.mark.document_type
def test_copy_fields_from__doc_type_from_template_to_template__only_template_fields_copied(
    test_document_type_with_template_and_llm_extractors: DocumentType,
):
    target_document_type = DocumentTypeFactory.create(
        tenant_id=uuid.uuid4().hex, name="target dt", extraction_type=ExtractionType.TEMPLATE
    )

    target_document_type.copy_fields_from(test_document_type_with_template_and_llm_extractors)

    source_extractor = next(
        filter(
            lambda ext: ext.type == ExtractorType.TEMPLATE,
            test_document_type_with_template_and_llm_extractors.extractors.values(),
        )
    )
    target_extractor = next(
        filter(
            lambda ext: ext.type == ExtractorType.TEMPLATE,
            test_document_type_with_template_and_llm_extractors.extractors.values(),
        )
    )
    assert len(target_document_type.extractors) == 1

    assert source_extractor.fields == target_extractor.fields


@pytest.mark.document_type
def test_copy_fields_from__doc_type_with_tempate_to_other_type__error(
    test_document_type_with_template_extractors: DocumentType,
):
    target_document_type = DocumentTypeFactory.create(tenant_id=uuid.uuid4().hex, name="target dt")
    with pytest.raises(InvariantViolation) as err:
        target_document_type.copy_fields_from(test_document_type_with_template_extractors)

    assert (
        err.value.args[FIRST_ELEMENT]
        == "Copying fields possible only for document types that have Template extraction type."
    )


@pytest.mark.document_type
def test_copy_fields_from__doc_type_exists_not_template__error(
    test_document_type_with_llm_and_plugin_extractors_with_fields: DocumentType,
):
    target_document_type = DocumentTypeFactory.create(tenant_id=uuid.uuid4().hex, name="target dt")

    with pytest.raises(InvariantViolation) as err:
        target_document_type.copy_fields_from(test_document_type_with_llm_and_plugin_extractors_with_fields)

    assert (
        err.value.args[FIRST_ELEMENT]
        == "Copying fields possible only for document types that have Template extraction type."
    )


@pytest.mark.document_type
def test_copy_fields_from__doc_type_with_attached_extractor__copied(
    test_document_type_with_template_extractors: DocumentType,
):
    target_document_type = DocumentTypeFactory.create(
        tenant_id=uuid.uuid4().hex, name="target dt", extraction_type=ExtractionType.TEMPLATE
    )
    target_document_type.copy_fields_from(test_document_type_with_template_extractors)

    assert target_document_type.composite_fields == test_document_type_with_template_extractors.composite_fields
    assert len(target_document_type.extractors) == len(test_document_type_with_template_extractors.extractors)


@pytest.mark.parametrize(
    "current_extractor_type,attached_extractor_type,expected_extraction_type",
    (
        (ExtractorType.LLM, ExtractorType.PLUGIN, ExtractionType.PLUGIN),
        (ExtractorType.LLM, ExtractorType.TEMPLATE, ExtractionType.TEMPLATE),
        (ExtractorType.LLM, ExtractorType.PROTOTYPE, ExtractionType.PROTOTYPE),
        (ExtractorType.PLUGIN, ExtractorType.PLUGIN, ExtractionType.PLUGIN),
    ),
)
@pytest.mark.document_type
def test_attach_extractor__attached(
    test_document_type: DocumentType,
    current_extractor_type: ExtractorType,
    attached_extractor_type: ExtractorType,
    expected_extraction_type: ExtractionType,
):
    test_document_type.attach_extractor(type_=current_extractor_type, fields=[])
    test_document_type.attach_extractor(type_=attached_extractor_type, fields=[])

    assert test_document_type.extraction_type == expected_extraction_type


@pytest.mark.parametrize(
    "current_extractor_type,attached_extractor_type",
    (
        (ExtractorType.PROTOTYPE, ExtractorType.PROTOTYPE),
        (ExtractorType.PROTOTYPE, ExtractorType.TEMPLATE),
        (ExtractorType.PROTOTYPE, ExtractorType.PLUGIN),
        (ExtractorType.TEMPLATE, ExtractorType.PROTOTYPE),
        (ExtractorType.TEMPLATE, ExtractorType.PLUGIN),
        (ExtractorType.TEMPLATE, ExtractorType.TEMPLATE),
        (ExtractorType.PLUGIN, ExtractorType.TEMPLATE),
        (ExtractorType.PLUGIN, ExtractorType.PROTOTYPE),
    ),
)
@pytest.mark.document_type
def test_attach_extractor__not_attached(
    test_document_type: DocumentType,
    current_extractor_type: ExtractorType,
    attached_extractor_type: ExtractorType,
):
    test_document_type.attach_extractor(type_=current_extractor_type, fields=[])

    with pytest.raises(AttachmentExtractorConflict):
        test_document_type.attach_extractor(type_=attached_extractor_type, fields=[])


@pytest.mark.parametrize(
    "current_extractor_type,attached_extractor_type",
    (
        (ExtractorType.PROTOTYPE, ExtractorType.LLM),
        (ExtractorType.TEMPLATE, ExtractorType.LLM),
        (ExtractorType.PLUGIN, ExtractorType.LLM),
    ),
)
@pytest.mark.document_type
def test_attach_llm_extractor__attached(
    test_document_type: DocumentType,
    current_extractor_type: ExtractorType,
    attached_extractor_type: ExtractorType,
):
    extractor1 = test_document_type.attach_extractor(type_=current_extractor_type, fields=[])

    extractor2 = test_document_type.attach_extractor(type_=attached_extractor_type, fields=[])

    assert len(test_document_type.extractors) == 2
    assert test_document_type.extractors[extractor1.id()].type == current_extractor_type
    assert test_document_type.extractors[extractor2.id()].type == attached_extractor_type


@pytest.mark.document_type
def test_attach_plugin_without_fields__attached(
    test_document_type: DocumentType,
):
    attached_extractor_type = ExtractorType.PLUGIN
    language = "test language"
    engine = "test engine"
    image_transformations = ["test image_transformation"]
    description = "test description"

    extractor = test_document_type.attach_extractor(
        type_=ExtractorType.PLUGIN,
        fields=[],
        language=language,
        engine=engine,
        image_transformations=image_transformations,
        description=description,
    )

    expected_events = [
        ExtractorAttached(
            extractor_id=test_document_type.extractors[extractor.id()].id(),
            document_type_id=test_document_type.id(),
            extraction_type=attached_extractor_type.value,
            language=language,
            engine=engine,
            image_transformations=image_transformations,
            description=description,
        )
    ]

    assert test_document_type.extraction_type == ExtractionType.PLUGIN
    assert test_document_type.events == expected_events


@pytest.mark.document_type
def test_attach_plugin_with_fields_and_params__attached(
    test_document_type: DocumentType,
    attach_extractor_fields: list[FieldAttachment],
):
    attached_extractor_type = ExtractorType.PLUGIN
    language = "test language"
    engine = "test engine"
    image_transformations = ["test image_transformation"]
    description = "test description"

    extractor = test_document_type.attach_extractor(
        type_=attached_extractor_type,
        fields=attach_extractor_fields,
        language=language,
        engine=engine,
        image_transformations=image_transformations,
        description=description,
    )
    expected_extractor_type = (
        test_document_type.extractors[extractor.id()].type
        if test_document_type.extractors[_get_extractor_id(test_document_type, FIRST_ELEMENT)].type != ExtractorType.LLM
        else ExtractionType.NON
    )
    expected_events = [
        ExtractorAttached(
            extractor_id=test_document_type.extractors[_get_extractor_id(test_document_type, FIRST_ELEMENT)].id(),
            document_type_id=test_document_type.id(),
            extraction_type=expected_extractor_type,
            language=language,
            engine=engine,
            image_transformations=image_transformations,
            description=description,
        ),
        ExtractorFieldCreated(
            code=attach_extractor_fields[0].code,
            name=attach_extractor_fields[0].name,
            document_type_code=test_document_type.id(),
            extractor_id=test_document_type.extractors[_get_extractor_id(test_document_type, FIRST_ELEMENT)].id(),
            extractor_type=expected_extractor_type.value,
            field_type=attach_extractor_fields[0].type,
            required=attach_extractor_fields[0].required,
            order=attach_extractor_fields[0].order,
            confidential=attach_extractor_fields[0].confidential,
            read_only=attach_extractor_fields[0].read_only,
            description=attach_extractor_fields[0].description,
        ),
    ]

    assert test_document_type.extraction_type == ExtractionType.PLUGIN
    assert test_document_type.events == expected_events


@pytest.mark.document_type
def test_attach_llm_extractor_to_plugin_extraction_type__attached__no_new_extractor_attached_event(
    test_document_type_with_plugin_extractor: DocumentType,
):
    language = "test language"
    engine = "test engine"
    image_transformations = ["test image_transformation"]
    description = "test description"

    test_document_type_with_plugin_extractor.attach_extractor(
        type_=ExtractorType.LLM,
        fields=[],
        language=language,
        engine=engine,
        image_transformations=image_transformations,
        description=description,
    )

    assert test_document_type_with_plugin_extractor.extraction_type == ExtractionType.PLUGIN
    assert test_document_type_with_plugin_extractor.events == []


@pytest.mark.document_type
def test_attach_plugin__track_fields_changes__old_fields_removed_new_added(
    test_document_type_plugin_extractor_with_field: DocumentType,
    attach_extractor_fields: list[FieldAttachment],
):
    attached_extractor_type = ExtractorType.PLUGIN
    language = "test language"
    engine = "test engine"
    image_transformations = ["test image_transformation"]
    description = "test description"

    test_document_type_plugin_extractor_with_field.attach_extractor(
        type_=attached_extractor_type,
        fields=attach_extractor_fields,
        language=language,
        engine=engine,
        image_transformations=image_transformations,
        description=description,
    )

    assert test_document_type_plugin_extractor_with_field.extraction_type.value == attached_extractor_type.value
    assert len(test_document_type_plugin_extractor_with_field.composite_fields) == len(attach_extractor_fields)


@pytest.mark.document_type
def test_attach_plugin__track_fields_changes__efield_changed__fields_updated(
    test_document_type_with_plugin_extractor: DocumentType,
):
    attached_extractor_type = ExtractorType.PLUGIN
    already_exists_field = test_document_type_with_plugin_extractor.add_field(**create_field_with_full_payload)
    field_to_update = FieldAttachment(
        name="new_name",
        code=already_exists_field.code(),
        required=not already_exists_field.required,
        order=already_exists_field.display_order + 1,
        confidential=already_exists_field.confidential,
        read_only=already_exists_field.read_only,
        type=already_exists_field.profile.type,
        description=StringFieldDescription(display_char_limit=100),
    )

    extractor = test_document_type_with_plugin_extractor.attach_extractor(
        type_=attached_extractor_type,
        fields=[field_to_update],
    )

    expected_update_event = ExtractorFieldUpdated(
        code=field_to_update.code,
        name=field_to_update.name,
        document_type_code=test_document_type_with_plugin_extractor.id(),
        extractor_id=extractor.id(),
        extractor_type=attached_extractor_type,
        field_type=field_to_update.type,
        required=field_to_update.required,
        order=field_to_update.order,
        confidential=field_to_update.confidential,
        read_only=field_to_update.read_only,
        description=field_to_update.description,
    )

    assert test_document_type_with_plugin_extractor.extraction_type == ExtractionType.PLUGIN
    assert len(test_document_type_with_plugin_extractor.composite_fields) == 1
    assert expected_update_event in test_document_type_with_plugin_extractor.events


@pytest.mark.document_type
def test_attach_plugin__track_fields_changes__compliency_policy_changed__fields_updated(
    test_document_type_with_plugin_extractor: DocumentType,
):
    attached_extractor_type = ExtractorType.PLUGIN
    already_exists_field = test_document_type_with_plugin_extractor.add_field(**create_field_with_full_payload)
    field_to_update = FieldAttachment(
        name=already_exists_field.name,
        code=already_exists_field.code(),
        required=already_exists_field.required,
        order=already_exists_field.display_order,
        confidential=not already_exists_field.confidential,
        read_only=not already_exists_field.read_only,
        type=already_exists_field.profile.type,
        description=already_exists_field.profile.description,
    )

    extractor = test_document_type_with_plugin_extractor.attach_extractor(
        type_=attached_extractor_type,
        fields=[field_to_update],
    )

    expected_update_event = ExtractorFieldUpdated(
        code=field_to_update.code,
        name=field_to_update.name,
        document_type_code=test_document_type_with_plugin_extractor.id(),
        extractor_id=extractor.id(),
        extractor_type=attached_extractor_type,
        field_type=field_to_update.type,
        required=field_to_update.required,
        order=field_to_update.order,
        confidential=field_to_update.confidential,
        read_only=field_to_update.read_only,
        description=field_to_update.description,
    )

    assert test_document_type_with_plugin_extractor.extraction_type == ExtractionType.PLUGIN
    assert len(test_document_type_with_plugin_extractor.composite_fields) == 1
    assert expected_update_event in test_document_type_with_plugin_extractor.events


@pytest.mark.document_type
def test_attach_plugin__track_fields_changes__old_fields_not_removed_new_added(
    test_document_type_llm_extractor_with_field: DocumentType,
    attach_extractor_fields: list[FieldAttachment],
):
    attached_extractor_type = ExtractorType.PLUGIN
    language = "test language"
    engine = "test engine"
    image_transformations = ["test image_transformation"]
    description = "test description"

    test_document_type_llm_extractor_with_field.attach_extractor(
        type_=attached_extractor_type,
        fields=attach_extractor_fields,
        language=language,
        engine=engine,
        image_transformations=image_transformations,
        description=description,
    )

    assert test_document_type_llm_extractor_with_field.extraction_type == ExtractionType.PLUGIN
    assert len(test_document_type_llm_extractor_with_field.composite_fields) == len(attach_extractor_fields) + 1


def test_attach_plugin__track_fields_changes__fields_the_same__no_update_events(
    test_document_type_plugin_extractor_with_field: DocumentType,
):
    attached_extractor_type = ExtractorType.PLUGIN
    already_exists_field = test_document_type_plugin_extractor_with_field.composite_fields[0]

    field_to_update = FieldAttachment(
        name=already_exists_field.name,
        code=already_exists_field.code(),
        required=already_exists_field.required,
        order=already_exists_field.display_order,
        confidential=already_exists_field.confidential,
        read_only=already_exists_field.read_only,
        type=already_exists_field.profile.type,
        description=already_exists_field.profile.description,
    )

    test_document_type_plugin_extractor_with_field.attach_extractor(
        type_=attached_extractor_type,
        fields=[field_to_update],
    )

    update_event = list(
        filter(
            lambda event: isinstance(event, ExtractorFieldUpdated),
            test_document_type_plugin_extractor_with_field.events,
        )
    )

    assert test_document_type_plugin_extractor_with_field.extraction_type == ExtractionType.PLUGIN
    assert len(test_document_type_plugin_extractor_with_field.composite_fields) == 1
    assert not update_event


def test_detach_extractor__ok(test_document_type_with_llm_and_plugin_extractors):
    extractor_for_detach = next(
        extractor
        for extractor in test_document_type_with_llm_and_plugin_extractors.extractors.values()
        if extractor.type == ExtractorType.LLM
    )

    assert len(test_document_type_with_llm_and_plugin_extractors.extractors) == 2

    test_document_type_with_llm_and_plugin_extractors.detach_extractor(extractor_for_detach.id())

    assert len(test_document_type_with_llm_and_plugin_extractors.extractors) == 1
    assert (
        test_document_type_with_llm_and_plugin_extractors.extractors[
            _get_extractor_id(test_document_type_with_llm_and_plugin_extractors, FIRST_ELEMENT)
        ]
        != extractor_for_detach
    )


def test_detach_extractor__wrong_extractor_type__error(test_document_type_with_llm_and_plugin_extractors):
    extractor_for_detach = next(
        extractor
        for extractor in test_document_type_with_llm_and_plugin_extractors.extractors.values()
        if extractor.type != ExtractorType.LLM
    )

    assert len(test_document_type_with_llm_and_plugin_extractors.extractors) == 2
    with pytest.raises(InvariantViolation):
        test_document_type_with_llm_and_plugin_extractors.detach_extractor(extractor_for_detach.id())

    assert len(test_document_type_with_llm_and_plugin_extractors.extractors) == 2


def test_detach_extractor__event_added(test_document_type_with_llm_and_plugin_extractors):
    extractor_for_detach = next(
        extractor
        for extractor in test_document_type_with_llm_and_plugin_extractors.extractors.values()
        if extractor.type == ExtractorType.LLM
    )
    test_document_type_with_llm_and_plugin_extractors.detach_extractor(extractor_for_detach.id())
    expected_event = ExtractorDetached(
        document_type_id=test_document_type_with_llm_and_plugin_extractors.id(),
        extractor_id=extractor_for_detach.id(),
        extractor_type=extractor_for_detach.type,
    )

    assert len(test_document_type_with_llm_and_plugin_extractors.events) == 1
    assert test_document_type_with_llm_and_plugin_extractors.events[FIRST_ELEMENT] == expected_event


def test_detach_extractor__wrong_extractor_id__errors(test_document_type_with_llm_and_plugin_extractors):
    with pytest.raises(ExtractorNotFound):
        test_document_type_with_llm_and_plugin_extractors.detach_extractor("fake_extarctor")


def test_detach_extractor__no_extractors__errors(test_document_type):
    with pytest.raises(ExtractorNotFound):
        test_document_type.detach_extractor("fake_extarctor")


def test_create_workflow_for__created(test_document_type_with_llm_extractors, perform_extraction_payload):
    workflow = test_document_type_with_llm_extractors.create_workflow_for(
        document_id=perform_extraction_payload["document_id"],
        tenant_id=perform_extraction_payload["tenant_id"],
        correlation_headers=perform_extraction_payload["correlation_headers"],
        extra_headers=perform_extraction_payload["extra_headers"],
        template_version_id=perform_extraction_payload["template_version_id"],
        language=perform_extraction_payload["language"],
        engine=perform_extraction_payload["document_id"],
        llm_type=perform_extraction_payload["llm_type"],
    )

    assert workflow


def test_create_workflow_for__only_required_args__created(
    test_document_type_with_llm_extractors, perform_extraction_payload
):
    workflow = test_document_type_with_llm_extractors.create_workflow_for(
        document_id=perform_extraction_payload["document_id"],
        tenant_id=perform_extraction_payload["tenant_id"],
        correlation_headers=perform_extraction_payload["correlation_headers"],
        extra_headers=perform_extraction_payload["extra_headers"],
    )

    assert workflow


@pytest.mark.parametrize(
    "document_type_fixture",
    [
        "test_document_type_with_llm_and_plugin_extractors",
        "test_document_type_with_llm_extractors",
        "test_document_type_with_template_extractors",
        "test_document_type_with_2_llm_and_plugin_extractors",
    ],
)
def test_create_workflow_for__steps_added(request, document_type_fixture, perform_extraction_payload):
    document_type = request.getfixturevalue(document_type_fixture)
    workflow = document_type.create_workflow_for(
        document_id=perform_extraction_payload["document_id"],
        tenant_id=perform_extraction_payload["tenant_id"],
        correlation_headers=perform_extraction_payload["correlation_headers"],
        extra_headers=perform_extraction_payload["extra_headers"],
        template_version_id=perform_extraction_payload["template_version_id"],
        language=perform_extraction_payload["language"],
        engine=perform_extraction_payload["engine"],
        llm_type=perform_extraction_payload["llm_type"],
    )

    assert (
        len(workflow.steps) == len(document_type.extractors) + 1
    )  # One is PerformExtractionReply for WorkflowManager service


def test_create_workflow_for__no_extractors__error(test_document_type, perform_extraction_payload):
    with pytest.raises(ExtractionWorkflowCreationError):
        test_document_type.create_workflow_for(
            document_id=perform_extraction_payload["document_id"],
            tenant_id=perform_extraction_payload["tenant_id"],
            correlation_headers=perform_extraction_payload["correlation_headers"],
            extra_headers=perform_extraction_payload["extra_headers"],
        )
