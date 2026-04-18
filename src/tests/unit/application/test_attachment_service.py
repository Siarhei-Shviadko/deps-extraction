import random
from typing import Any

import pytest

from deps_extraction.application import AttachmentService, DocumentTypeService
from deps_extraction.domain.events import ExtractorAttached
from deps_extraction.domain.exceptions import AttachmentExtractorConflict
from deps_extraction.domain.interfaces.repositories.document_type import (
    IDocumentTypeRepository,
)
from deps_extraction.domain.model import (
    AttachmentInfo,
    DocumentType,
    ExtractorType,
    FieldAttachment,
    FieldType,
    RawUpdateField,
)


@pytest.mark.attach_extractor
def test_attach_extractor__document_type_exist__saved(
    test_document_type: DocumentType,
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields: list[FieldAttachment],
    test_tenant: str,
) -> None:
    fake_document_type_repository.save(test_document_type)

    attachment_info = attachment_service.attach_extractor(
        document_type_name=test_document_type.name,
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields,
    )

    assert attachment_info.command_channel == test_document_type.command_channel
    assert attachment_info.document_type_id == test_document_type.id()


@pytest.mark.attach_extractor
def test_attach_second_extractor__ok(
    test_document_type_with_llm_extractors: DocumentType,
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields: list[FieldAttachment],
    test_tenant: str,
) -> None:
    fake_document_type_repository.save(test_document_type_with_llm_extractors)
    attachment_info = attachment_service.attach_extractor(
        document_type_name=test_document_type_with_llm_extractors.name,
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields,
    )

    saved_doc_type = fake_document_type_repository.find_by_id_for_tenant(
        document_type_id=test_document_type_with_llm_extractors.id(),
        tenant_id=test_document_type_with_llm_extractors.tenant_id(),
    )
    assert attachment_info.command_channel == test_document_type_with_llm_extractors.command_channel
    assert attachment_info.document_type_id == test_document_type_with_llm_extractors.id()


@pytest.mark.attach_extractor
def test_attach_extractor__reuse_with_different_type__error(
    test_document_type_with_llm_extractors: DocumentType,
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields: list[FieldAttachment],
    test_tenant: str,
) -> None:
    fake_document_type_repository.save(test_document_type_with_llm_extractors)
    attachment_info = attachment_service.attach_extractor(
        document_type_name=test_document_type_with_llm_extractors.name,
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields,
    )
    with pytest.raises(AttachmentExtractorConflict):
        attachment_service.attach_extractor(
            document_type_name=test_document_type_with_llm_extractors.name,
            tenant_id=test_tenant,
            extractor_type=ExtractorType.PROTOTYPE,
            description=attach_extractor_request["description"],
            engine=attach_extractor_request["engine"],
            language=attach_extractor_request["language"],
            image_transformations=attach_extractor_request["imageTransformations"],
            fields=attach_extractor_fields,
            extractor_id=attachment_info.extractor_id,
        )


@pytest.mark.attach_extractor
def test_attach_extractor__document_type__not_exist__saved(
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields: list[FieldAttachment],
    test_tenant: str,
) -> None:
    new_document_type_name = "test document_type"
    attachment_info = attachment_service.attach_extractor(
        document_type_name=new_document_type_name,
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields,
    )

    assert attachment_info.command_channel == f"{new_document_type_name}-{test_tenant}"


@pytest.mark.attach_extractor
def test_perform_attachment_plugin__document_type_exist__saved(
    test_document_type: DocumentType,
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_fields: list[FieldAttachment],
) -> None:
    attachment_info = attachment_service.perform_attachment(
        document_type=test_document_type,
        extractor_type=ExtractorType.PLUGIN,
        fields=attach_extractor_fields,
    )

    saved_document_type = fake_document_type_repository.get(test_document_type.id())

    assert attachment_info.command_channel == saved_document_type.command_channel
    assert attachment_info.document_type_id == saved_document_type.id()


@pytest.mark.attach_extractor
def test_attach_extractor__document_type_doesnt_exist__order_accrording_place_in_list(
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_fields_without_orders: list[FieldAttachment],
    attached_extractor_info: AttachmentInfo,
    test_tenant: str,
) -> None:
    saved_doc_type = fake_document_type_repository.find_by_id_for_tenant(
        attached_extractor_info.document_type_id, test_tenant
    )
    expected_order = [el.code for el in attach_extractor_fields_without_orders]

    assert expected_order == [field.code() for field in saved_doc_type.extraction_fields]


@pytest.mark.attach_extractor
def test_attach_extractor__document_type_exists__add_new_fields__added_at_the_end(
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields_without_orders: list[FieldAttachment],
    test_tenant: str,
) -> None:
    first_part_of_fields = attach_extractor_fields_without_orders[:5]
    attachment_info = attachment_service.attach_extractor(
        document_type_name="test_name",
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=first_part_of_fields,
    )

    attachment_service.attach_extractor(
        document_type_name="test_name",
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields_without_orders,
    )

    saved_doc_type = fake_document_type_repository.find_by_id_for_tenant(attachment_info.document_type_id, test_tenant)
    expected_order = [el.code for el in attach_extractor_fields_without_orders]

    assert expected_order == [field.code() for field in saved_doc_type.extraction_fields]


@pytest.mark.attach_extractor
def test_attach_extractor__document_type_exists__fields_in_other_order__order_doesnt_changed(
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields_without_orders: list[FieldAttachment],
    test_tenant: str,
    attached_extractor_info: AttachmentInfo,
) -> None:
    attachment_service.attach_extractor(
        document_type_name="test_name",
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=list(reversed(attach_extractor_fields_without_orders)),
    )

    saved_doc_type = fake_document_type_repository.find_by_id_for_tenant(
        attached_extractor_info.document_type_id, test_tenant
    )
    expected_order = [el.code for el in attach_extractor_fields_without_orders]

    assert expected_order == [field.code() for field in saved_doc_type.extraction_fields]


@pytest.mark.attach_extractor
def test_attach_extractor__document_type_exists__add_less_fields__order_saved(
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields_without_orders: list[FieldAttachment],
    attached_extractor_info: AttachmentInfo,
    test_tenant: str,
) -> None:
    attachment_service.attach_extractor(
        document_type_name="test_name",
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields_without_orders[::2],
    )

    saved_doc_type = fake_document_type_repository.find_by_id_for_tenant(
        attached_extractor_info.document_type_id, test_tenant
    )
    expected_order = [el.code for el in attach_extractor_fields_without_orders[::2]]

    assert expected_order == [field.code() for field in saved_doc_type.extraction_fields]


@pytest.mark.attach_extractor
def test_attach_extractor__fields_ordered_in_custom_way__order_doesnt_changed(
    attachment_service: AttachmentService,
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields_without_orders: list[FieldAttachment],
    attached_extractor_info: AttachmentInfo,
    test_tenant: str,
) -> None:
    doc_type_id = attached_extractor_info.document_type_id

    ordered_fields = sorted(
        [
            RawUpdateField(
                code=field.code,
                name=field.name,
                required=field.required,
                order=random.randint(1, 10),
                confidential=field.confidential,
                read_only=field.read_only,
                description=field.description,
            )
            for field in attach_extractor_fields_without_orders
        ],
        key=lambda f: f["order"],
    )
    document_type_service.update_fields(document_type_id=doc_type_id, tenant_id=test_tenant, fields=ordered_fields)

    attachment_service.attach_extractor(
        document_type_name="test_name",
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields_without_orders,
    )

    saved_doc_type = fake_document_type_repository.find_by_id_for_tenant(
        attached_extractor_info.document_type_id, test_tenant
    )
    expected_order = [el["code"] for el in ordered_fields]

    assert expected_order == [
        field.code() for field in sorted(saved_doc_type.extraction_fields, key=lambda f: f.display_order)
    ]
    assert expected_order != [field.code for field in attach_extractor_fields_without_orders]


@pytest.mark.attach_extractor
def test_attach_extractor__fields_in_default_order__new_fields_with_order_added__order_saved(
    attachment_service: AttachmentService,
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields_without_orders: list[FieldAttachment],
    attached_extractor_info: AttachmentInfo,
    attached_llm_extractor_info: AttachmentInfo,
    attach_llm_extractor_fields_without_orders,
    test_tenant: str,
) -> None:
    doc_type_id = attached_llm_extractor_info.document_type_id
    extractor_id = attached_llm_extractor_info.extractor_id

    field_2 = document_type_service.create_field(
        document_type_id=doc_type_id,
        tenant_id=test_tenant,
        name="new_field_2",
        type_=FieldType.STRING,
        required=False,
        order=2,
        extractor_id=extractor_id,
    )

    field_1 = document_type_service.create_field(
        document_type_id=doc_type_id,
        tenant_id=test_tenant,
        name="new_field_1",
        type_=FieldType.STRING,
        required=False,
        order=1,
        extractor_id=extractor_id,
    )

    attachment_service.attach_extractor(
        document_type_name="test_name",
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields_without_orders,
    )

    saved_doc_type = fake_document_type_repository.find_by_id_for_tenant(doc_type_id, test_tenant)
    expected_order = (
        [el.code for el in attach_extractor_fields_without_orders]
        + [el.code for el in attach_llm_extractor_fields_without_orders]
        + [field_2.code(), field_1.code()]
    )

    assert expected_order == [field.code() for field in saved_doc_type.extraction_fields]


@pytest.mark.attach_extractor
def test_attach_extractor__fields_in_default_order__fields_order_updated__order_saved(
    attachment_service: AttachmentService,
    document_type_service: DocumentTypeService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields_without_orders: list[FieldAttachment],
    attached_extractor_info: AttachmentInfo,
    test_tenant: str,
) -> None:
    doc_type_id = attached_extractor_info.document_type_id
    extractor_id = attached_extractor_info.extractor_id

    document_type_service.update_field(
        document_type_id=doc_type_id,
        tenant_id=test_tenant,
        code=attach_extractor_fields_without_orders[3].code,
        name="UPDATED FIELD 2",
        required=False,
        order=2,
        extractor_id=extractor_id,
    )

    document_type_service.update_field(
        document_type_id=doc_type_id,
        tenant_id=test_tenant,
        name="UPDATED FIELD 1",
        code=attach_extractor_fields_without_orders[4].code,
        required=False,
        order=1,
        extractor_id=extractor_id,
    )

    attachment_service.attach_extractor(
        document_type_name="test_name",
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields_without_orders,
    )

    saved_doc_type = fake_document_type_repository.find_by_id_for_tenant(doc_type_id, test_tenant)

    expected_order = [el.code for el in attach_extractor_fields_without_orders if el.code]

    assert expected_order == [field.code() for field in saved_doc_type.extraction_fields]


@pytest.mark.attach_extractor
def test_attach_extractor__extractor_type_is_none__document_type_created_without_extractors(
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields: list[FieldAttachment],
    test_tenant: str,
) -> None:
    doc_name = "new_doc_type"
    attachment_info = attachment_service.attach_extractor(
        document_type_name=doc_name,
        tenant_id=test_tenant,
        extractor_type=None,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields,
    )
    saved_doc_type = fake_document_type_repository.get(attachment_info.document_type_id)

    assert saved_doc_type
    assert saved_doc_type.extractors == {}
    assert saved_doc_type.events == []


@pytest.mark.attach_extractor
def test_attach_llm_extractor__to_non_document_type__extractor_attached(
    attachment_service: AttachmentService,
    fake_document_type_repository: IDocumentTypeRepository,
    attach_extractor_request: dict[str, Any],
    attach_extractor_fields: list[FieldAttachment],
    attach_extractor_fields_2: list[FieldAttachment],
    test_tenant: str,
) -> None:
    doc_name = "new_doc_type"
    attachment_info = attachment_service.attach_extractor(
        document_type_name=doc_name,
        tenant_id=test_tenant,
        extractor_type=None,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields,
    )

    attachment_service.attach_extractor(
        document_type_name=doc_name,
        tenant_id=test_tenant,
        extractor_type=ExtractorType.LLM,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields_2,
    )
    saved_doc_type = fake_document_type_repository.get(attachment_info.document_type_id)

    assert saved_doc_type
    assert len(saved_doc_type.extractors) == 1
    assert len(list(filter(lambda event: isinstance(event, ExtractorAttached), saved_doc_type.events))) == 1
