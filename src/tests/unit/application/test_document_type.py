from typing import Any
from uuid import uuid4

import pytest

from deps_extraction.application import DocumentTypeService
from deps_extraction.domain.events import ExtractDocument
from deps_extraction.domain.exceptions import (
    DocumentTypeNotFound,
    ExtractionWorkflowCreationError,
    ExtractorNotFound,
    InvariantViolation,
)
from deps_extraction.domain.interfaces import IDocumentTypeRepository
from deps_extraction.domain.model import (
    Code,
    DocumentType,
    DocumentTypeFactory,
    ExtractionType,
    ExtractorType,
    RawUpdateField,
)
from tests.data import raw_prototype_document_type
from tests.factories import ExtractionFieldFactory

FIRST_ELEMENT = 0


def test_save_new_document_type__doc_type_doesnt_exist__saved(
    raw_document_type,
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
):
    document_type_service.save_new_document_type(
        document_type_id=raw_document_type["document_type_id"],
        tenant_id=raw_document_type["tenant_id"],
        name=raw_document_type["name"],
    )

    created_doc_type = fake_document_type_repository.get(raw_document_type["document_type_id"])

    assert raw_document_type["document_type_id"] == created_doc_type.id()
    assert raw_document_type["tenant_id"] == created_doc_type.tenant_id()
    assert raw_document_type["name"] == created_doc_type.name


def test_save_new_document_type__doc_type_exists__not_updated(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
):
    old_doc_type_name = raw_prototype_document_type["name"]
    document_type_service.save_new_document_type(
        document_type_id=raw_prototype_document_type["document_type_id"],
        tenant_id=raw_prototype_document_type["tenant_id"],
        name=raw_prototype_document_type["name"],
    )
    raw_prototype_document_type["name"] = uuid4().hex

    document_type_service.save_new_document_type(
        document_type_id=raw_prototype_document_type["document_type_id"],
        tenant_id=raw_prototype_document_type["tenant_id"],
        name=raw_prototype_document_type["name"],
    )

    updated_doc_type = fake_document_type_repository.get(raw_prototype_document_type["document_type_id"])
    assert updated_doc_type.name == old_doc_type_name


def test_save_document_type__doc_type_doesnt_exist__saved(
    raw_document_type,
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
):
    document_type_service.save_document_type(
        document_type_id=raw_document_type["document_type_id"],
        tenant_id=raw_document_type["tenant_id"],
        name=raw_document_type["name"],
    )

    created_doc_type = fake_document_type_repository.get(raw_document_type["document_type_id"])

    assert created_doc_type.id() == raw_document_type["document_type_id"]
    assert created_doc_type.tenant_id() == raw_document_type["tenant_id"]
    assert created_doc_type.name == raw_document_type["name"]
    assert created_doc_type.extraction_type == ExtractionType.NON


def test_extract_document__command_sent(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type_plugin_extractor_with_field,
    fake_message_producer,
    test_tenant,
):
    fake_document_type_repository.save(test_document_type_plugin_extractor_with_field)

    document_type_service.extract_document(
        document_id=str(1),
        document_type_id=test_document_type_plugin_extractor_with_field.id.id,
        tenant_id=test_tenant,
        correlation_headers={"commandreply_reply_to": "test"},
        extra_headers={},
    )

    command = fake_message_producer[FIRST_ELEMENT]
    assert len(fake_message_producer) == 1
    assert command.destination == test_document_type_plugin_extractor_with_field.command_channel
    assert command.message.headers["command_type"] == ExtractDocument.__name__


def test_extract_document__no_extractors__error(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type,
):
    test_document_type.extractor_type = ExtractorType.PLUGIN
    fake_document_type_repository.save(test_document_type)
    test_document_id = "123456"

    with pytest.raises(ExtractionWorkflowCreationError):
        document_type_service.extract_document(
            document_id=test_document_id,
            document_type_id=test_document_type.id.id,
            tenant_id=test_document_type.tenant_id(),
            correlation_headers={"commandreply_reply_to": "test"},
            extra_headers={},
        )


def test_save_new_document_types__doc_types_dont_exist__saved(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    messaging__raw_document_types,
):
    document_type_service.save_new_document_types(messaging__raw_document_types)

    for doc_type in messaging__raw_document_types:
        result = fake_document_type_repository.get(doc_type["document_type_id"])
        assert doc_type["document_type_id"] == result.id()
        assert doc_type["tenant_id"] == result.tenant_id()


def test_save_new_document_types__doc_types_exist__not_updated(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    messaging__raw_document_types,
):
    new_doc_type_name = uuid4().hex
    document_type_service.save_new_document_types(messaging__raw_document_types)

    for doc_type in messaging__raw_document_types:
        doc_type["name"] = new_doc_type_name

    document_type_service.save_new_document_types(messaging__raw_document_types)

    for doc_type in messaging__raw_document_types:
        result = fake_document_type_repository.get(doc_type["document_type_id"])
        assert result.name != new_doc_type_name


def test_delete_document_type__success(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type,
):
    fake_document_type_repository.save(test_document_type)
    document_type_service.delete_document_type(test_document_type.id(), test_document_type.tenant_id())

    remained_document_type = fake_document_type_repository.get(test_document_type.id())

    assert remained_document_type is None


def test_delete_document_type__not_found(document_type_service, test_document_type):
    with pytest.raises(DocumentTypeNotFound):
        document_type_service.delete_document_type(test_document_type.id(), test_document_type.tenant_id())


def test_get_document_types_by_tenant__success(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type,
):
    fake_document_type_repository.save(test_document_type)
    test_result = document_type_service.get_document_types(tenant_id=test_document_type.tenant_id())

    assert len(test_result) == 1
    assert test_document_type == test_result[0]


def test_get_document_type_by_tenant__success(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type,
):
    fake_document_type_repository.save(test_document_type)
    document_type = document_type_service.get_document_type(
        document_type_id=test_document_type.id(), tenant_id=test_document_type.tenant_id()
    )

    assert document_type == test_document_type


def test_get_document_type_by_tenant__not_found(
    document_type_service,
    test_id,
    test_document_type,
):
    with pytest.raises(DocumentTypeNotFound):
        document_type_service.get_document_type(
            document_type_id=test_document_type.id(), tenant_id=test_document_type.tenant_id()
        )


@pytest.mark.current_test
def test_update_field__field_exist__success(
    fake_document_type_repository: IDocumentTypeRepository,
    test_tenant,
    document_type_service,
    test_document_type_with_llm_and_plugin_extractors_with_fields,
):
    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors_with_fields)

    extractor = next((e for e in test_document_type_with_llm_and_plugin_extractors_with_fields.extractors.values()))
    field_code_to_update = extractor.fields[0].code()
    new_name = "new name"

    updated_field = document_type_service.update_field(
        document_type_id=test_document_type_with_llm_and_plugin_extractors_with_fields.id(),
        tenant_id=test_document_type_with_llm_and_plugin_extractors_with_fields.tenant_id(),
        code=field_code_to_update,
        name=new_name,
        extractor_id=extractor.id(),
    )

    assert updated_field.code() == field_code_to_update
    assert updated_field.name == new_name
    assert (
        updated_field.required
        == test_document_type_with_llm_and_plugin_extractors_with_fields.extraction_fields[0].required
    )


def test_save_extraction_field__success(
    fake_document_type_repository: IDocumentTypeRepository,
    document_type_service: DocumentTypeService,
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)

    extractor = next((e for e in test_document_type_with_llm_and_plugin_extractors.extractors.values()))
    test_field = ExtractionFieldFactory()

    document_type_service.create_field(
        document_type_id=test_document_type_with_llm_and_plugin_extractors.id(),
        tenant_id=test_document_type_with_llm_and_plugin_extractors.tenant_id(),
        name=test_field.name,
        type_=test_field.profile.type,
        required=test_field.required,
        description=test_field.profile.description,
        code=test_field.code(),
        order=test_field.display_order,
        extractor_id=extractor.id(),
    )

    document_type = fake_document_type_repository.get(
        document_type_id=test_document_type_with_llm_and_plugin_extractors.id()
    )

    assert document_type.extraction_fields[FIRST_ELEMENT] == test_field


def test_save_extraction_field__doc_type_not_exist__not_saved(
    test_id,
    test_tenant,
    document_type_service: DocumentTypeService,
):
    extraction_field = ExtractionFieldFactory()

    with pytest.raises(DocumentTypeNotFound):
        document_type_service.create_field(
            document_type_id=test_id,
            tenant_id=test_tenant,
            name=extraction_field.name,
            type_=extraction_field.profile.type,
            required=extraction_field.required,
            code=extraction_field.code(),
            order=0,
            extractor_id=None,
        )


def test_create_field__document_type_doesnt_exist__error(
    test_id,
    test_tenant,
    create_field_request,
    document_type_service: DocumentTypeService,
):
    with pytest.raises(DocumentTypeNotFound):
        document_type_service.create_field(
            document_type_id=test_id,
            tenant_id=test_tenant,
            name=create_field_request["name"],
            type_=create_field_request["type"],
            required=create_field_request["required"],
            order=create_field_request["order"],
            extractor_id=None,
        )


def test_create_field__document_type_no_extractor__success(
    test_id,
    test_tenant,
    create_field_with_request_2,  # rename
    test_document_type_with_llm_extractors,
    fake_document_type_repository: IDocumentTypeRepository,
    document_type_service: DocumentTypeService,
):
    fake_document_type_repository.save(test_document_type_with_llm_extractors)
    extractor_id = next((e for e in test_document_type_with_llm_extractors.extractors.values())).id()

    created_field = document_type_service.create_field(
        document_type_id=test_id,
        tenant_id=test_tenant,
        name=create_field_with_request_2["name"],
        type_=create_field_with_request_2["type"],
        required=create_field_with_request_2["required"],
        order=create_field_with_request_2["order"],
        extractor_id=extractor_id,
    )

    assert created_field.name == create_field_with_request_2["name"]
    assert created_field.profile.type == create_field_with_request_2["type"]
    assert created_field.required == create_field_with_request_2["required"]
    assert created_field.display_order == create_field_with_request_2["order"]


def test_update_field__document_type_no_extractor__success(
    test_id,
    test_tenant,
    update_field_request_2,
    test_document_type_llm_extractor_with_field,
    fake_document_type_repository: IDocumentTypeRepository,
    document_type_service: DocumentTypeService,
):
    fake_document_type_repository.save(test_document_type_llm_extractor_with_field)
    field = test_document_type_llm_extractor_with_field.extraction_fields[0]
    extractor_id = next((e for e in test_document_type_llm_extractor_with_field.extractors.values())).id()

    updated_field = document_type_service.update_field(
        document_type_id=test_id,
        tenant_id=test_tenant,
        code=field.code(),
        name=update_field_request_2["name"],
        required=update_field_request_2["required"],
        confidential=update_field_request_2["confidential"],
        read_only=update_field_request_2["read_only"],
        extractor_id=extractor_id,
    )

    assert updated_field.name == update_field_request_2["name"]
    assert updated_field.required == update_field_request_2["required"]
    assert updated_field.confidential == update_field_request_2["confidential"]
    assert updated_field.read_only == update_field_request_2["read_only"]


def test_delete_field__document_type_no_extractor__success(
    test_id,
    test_tenant,
    test_document_type_llm_extractor_with_field,
    fake_document_type_repository: IDocumentTypeRepository,
    document_type_service: DocumentTypeService,
):
    fake_document_type_repository.save(test_document_type_llm_extractor_with_field)
    field = test_document_type_llm_extractor_with_field.extraction_fields[0]

    document_type_service.delete_fields(
        document_type_id=test_id,
        tenant_id=test_tenant,
        field_codes=[field.code()],
    )

    document_type = fake_document_type_repository.find_by_id_for_tenant(
        test_document_type_llm_extractor_with_field.id(), test_document_type_llm_extractor_with_field.tenant_id()
    )

    assert document_type.composite_fields == []


def test_copy_fields_extractors_exists__success(
    test_tenant: str,
    test_document_type_with_template_extractors_and_fields: DocumentType,
    fake_document_type_repository: IDocumentTypeRepository,
    document_type_service: DocumentTypeService,
):
    test_document_type = DocumentTypeFactory.create(
        id_=uuid4().hex, tenant_id=test_tenant, name="target dt", extraction_type=ExtractionType.TEMPLATE
    )

    fake_document_type_repository.save(test_document_type)
    fake_document_type_repository.save(test_document_type_with_template_extractors_and_fields)

    document_type_service.copy_fields(
        tenant_id=test_tenant,
        source_document_type_id=test_document_type_with_template_extractors_and_fields.id(),
        target_document_type_id=test_document_type.id(),
    )

    target_document_type = fake_document_type_repository.find_by_id_for_tenant(
        document_type_id=test_document_type.id(),
        tenant_id=test_tenant,
    )

    assert (
        target_document_type.composite_fields == test_document_type_with_template_extractors_and_fields.composite_fields
    )


def test_copy_fields_source_extractor_not_exists__error(
    test_tenant: str,
    test_document_type_llm_extractor_with_field: DocumentType,
    fake_document_type_repository: IDocumentTypeRepository,
    document_type_service: DocumentTypeService,
):
    test_document_type = DocumentTypeFactory.create(id_=uuid4().hex, tenant_id=test_tenant, name="target dt")
    fake_document_type_repository.save(test_document_type)

    with pytest.raises(DocumentTypeNotFound):
        document_type_service.copy_fields(
            tenant_id=test_tenant,
            source_document_type_id=test_document_type_llm_extractor_with_field.id(),
            target_document_type_id=test_document_type.id(),
        )


def test_copy_fields_target_extractor_not_exists__error(
    test_id: str,
    test_tenant: str,
    test_document_type_llm_extractor_with_field: DocumentType,
    fake_document_type_repository: IDocumentTypeRepository,
    document_type_service: DocumentTypeService,
):
    test_document_type = DocumentTypeFactory.create(id_=uuid4().hex, tenant_id=test_tenant, name="target dt")
    fake_document_type_repository.save(test_document_type_llm_extractor_with_field)

    with pytest.raises(DocumentTypeNotFound):
        document_type_service.copy_fields(
            tenant_id=test_tenant,
            source_document_type_id=test_document_type_llm_extractor_with_field.id(),
            target_document_type_id=test_document_type.id(),
        )


def test_update_fields__document_type_not_exists__error(
    test_document_type: DocumentType,
    document_type_service: DocumentTypeService,
):
    with pytest.raises(DocumentTypeNotFound):
        document_type_service.update_fields(
            document_type_id=test_document_type.id(), tenant_id=test_document_type.tenant_id(), fields=[]
        )


def test_update_fields__document_type_exists__field_not_exists__error(
    update_field_request: dict[str, Any],
    test_document_type_with_plugin_extractor: DocumentType,
    fake_document_type_repository: IDocumentTypeRepository,
    document_type_service: DocumentTypeService,
):
    fake_document_type_repository.save(test_document_type_with_plugin_extractor)
    update_field_request["code"] = Code()()

    with pytest.raises(ExtractorNotFound):
        document_type_service.update_fields(
            document_type_id=test_document_type_with_plugin_extractor.id(),
            tenant_id=test_document_type_with_plugin_extractor.tenant_id(),
            fields=[RawUpdateField(**update_field_request, description=None)],
        )


def test_update_fields_document_type_exists__field_exists__success(
    update_field_request_2: dict[str, Any],
    test_document_type_llm_extractor_with_field,
    fake_document_type_repository: IDocumentTypeRepository,
    document_type_service: DocumentTypeService,
):
    fake_document_type_repository.save(test_document_type_llm_extractor_with_field)
    field = test_document_type_llm_extractor_with_field.extraction_fields[0]
    update_field_request_2["code"] = field.code()

    updated_fields = document_type_service.update_fields(
        document_type_id=test_document_type_llm_extractor_with_field.id(),
        tenant_id=test_document_type_llm_extractor_with_field.tenant_id(),
        fields=[RawUpdateField(**update_field_request_2, description=None)],
    )

    assert updated_fields[0].name == update_field_request_2["name"]
    assert updated_fields[0].required == update_field_request_2["required"]
    assert updated_fields[0].confidential == update_field_request_2["confidential"]
    assert updated_fields[0].read_only == update_field_request_2["read_only"]


def test_detach_extractor__extractor_detached(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type_with_llm_and_plugin_extractors,
    test_tenant,
):
    target_extractor_id = list(test_document_type_with_llm_and_plugin_extractors.extractors.values())[0].id()
    target_doc_type_id = test_document_type_with_llm_and_plugin_extractors.id()
    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)

    assert target_extractor_id in [
        extractor.id() for extractor in test_document_type_with_llm_and_plugin_extractors.extractors.values()
    ]

    document_type_service.detach_extractor(
        document_type_id=target_doc_type_id, extractor_id=target_extractor_id, tenant_id=test_tenant
    )
    updated_doc = fake_document_type_repository.get(target_doc_type_id)

    assert len(updated_doc.extractors) == 1
    assert target_extractor_id not in [extractor.id() for extractor in updated_doc.extractors.values()]


def test_detach_extractor__wrong_doc_type_id__no_errors(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type_with_llm_and_plugin_extractors,
    test_tenant,
):
    target_extractor_id = list(test_document_type_with_llm_and_plugin_extractors.extractors.values())[0].id()
    target_doc_type_id = test_document_type_with_llm_and_plugin_extractors.id()
    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)

    assert target_extractor_id in [
        extractor.id() for extractor in test_document_type_with_llm_and_plugin_extractors.extractors.values()
    ]

    document_type_service.detach_extractor(
        document_type_id="fake_id", extractor_id=target_extractor_id, tenant_id=test_tenant
    )
    updated_doc = fake_document_type_repository.get(target_doc_type_id)

    assert len(updated_doc.extractors) == 2
    assert target_extractor_id in [extractor.id() for extractor in updated_doc.extractors.values()]


def test_detach_extractor__wrong_extractor_id__no_errors(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type_with_llm_and_plugin_extractors,
    test_tenant,
):
    target_extractor_id = list(test_document_type_with_llm_and_plugin_extractors.extractors.values())[0].id()
    target_doc_type_id = test_document_type_with_llm_and_plugin_extractors.id()
    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)

    assert target_extractor_id in [
        extractor.id() for extractor in test_document_type_with_llm_and_plugin_extractors.extractors.values()
    ]

    document_type_service.detach_extractor(
        document_type_id=target_doc_type_id, extractor_id="fake_id", tenant_id=test_tenant
    )
    updated_doc = fake_document_type_repository.get(target_doc_type_id)

    assert len(updated_doc.extractors) == 2
    assert target_extractor_id in [extractor.id() for extractor in updated_doc.extractors.values()]


def test_detach_extractor__not_llm_type__error(
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    test_document_type_with_llm_and_plugin_extractors,
    test_tenant,
):
    target_extractor_id = list(test_document_type_with_llm_and_plugin_extractors.extractors.values())[1].id()
    target_doc_type_id = test_document_type_with_llm_and_plugin_extractors.id()
    fake_document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)

    assert target_extractor_id in [
        extractor.id() for extractor in test_document_type_with_llm_and_plugin_extractors.extractors.values()
    ]
    assert list(test_document_type_with_llm_and_plugin_extractors.extractors.values())[1].type != ExtractorType.LLM

    with pytest.raises(InvariantViolation):
        document_type_service.detach_extractor(
            document_type_id=target_doc_type_id, extractor_id=target_extractor_id, tenant_id=test_tenant
        )


def test_get_all_extraction_fields(
    fake_document_type_repository,
    document_type_factory,
    document_type_service: DocumentTypeService,
):
    document_types = [document_type_factory(extractor_size=2) for _ in range(10)]

    document_types_mapping = {dt.id(): dt for dt in document_types}

    fake_document_type_repository.save_all(document_types)

    fields_data = document_type_service.get_all_extraction_fields()

    for field_data in fields_data:
        document_type = document_types_mapping.get(field_data["document_type_id"])

        assert document_type

        assert document_type.has_field_with_code(field_data["code"])

        field = document_type.find_field_with_code(field_data["code"])

        assert field_data["code"] == field.code()
        assert field_data["name"] == field.name
        assert field_data["required"] == field.required
        assert field_data["order"] == field.display_order
        assert field_data["description"] == field.description.to_dict()
