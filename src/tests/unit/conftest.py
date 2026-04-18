import random
from typing import Any
from uuid import uuid4

import pytest
from deps_message_flow.commands.consumer import CommandMessage

from deps_extraction.api.serializers import SerializedField
from deps_extraction.domain.events import GetDocumentTypesReply
from deps_extraction.domain.model import (
    AttachmentInfo,
    ExtractorType,
    FieldAttachment,
    FieldType,
)
from tests.data import (
    raw_document_type_without_extraction_type,
    raw_plugin_document_type,
    raw_prototype_document_type,
    raw_template_document_type,
)
from tests.factories.document_type.profile import *
from tests.fakes import (
    FakeDocumentTypeProxy,
    FakeDocumentTypeRepository,
    FakeExtractedDataRepository,
    FakeExtractionWorkflowRepository,
    FakeMessageProducer,
    FakeSagaInstanceRepository,
)


@pytest.fixture
def application(containers):
    with containers.reset_singletons():
        application = containers.application()
        yield application


@pytest.fixture
def attachment_service(containers):
    return containers.attachment_service()


@pytest.fixture
def document_type_service(application):
    return application.document_type()


@pytest.fixture
def postgres_datasource_mock(mocker, containers):
    mock = mocker.Mock(containers.datasources.postgres_datasource())
    containers.datasources.postgres_datasource.override(mock)

    yield mock

    containers.datasources.reset_override()


@pytest.fixture(autouse=True)
def fake_document_type_repository(repositories):
    with repositories.document_type.override(FakeDocumentTypeRepository()):
        yield repositories.document_type()


@pytest.fixture(autouse=True)
def fake_extracted_data_repository(repositories):
    with repositories.extracted_data.override(FakeExtractedDataRepository()):
        yield repositories.extracted_data()


@pytest.fixture(autouse=True)
def fake_extraction_workflow_repository(repositories):
    with repositories.extraction_workflow.override(FakeExtractionWorkflowRepository()):
        yield repositories.extraction_workflow()


@pytest.fixture(autouse=True)
def fake_document_type_proxy(containers):
    with containers.external_services.document_type.override(FakeDocumentTypeProxy()) as dep:
        yield dep()


@pytest.fixture(autouse=True)
def fake_message_producer(containers, messaging):
    produced_messages = []
    fake_producer = FakeMessageProducer(produced_messages)

    with messaging.producer.override(fake_producer):
        containers.reset_singletons()
        yield produced_messages
        produced_messages.clear()


@pytest.fixture(autouse=True)
def fake_saga_instance_repository(containers):
    with containers.repositories.saga_instance.override(FakeSagaInstanceRepository()) as dep:
        yield dep()


@pytest.fixture
def saved_extracted_data(extracted_data_factory, fake_extracted_data_repository):
    edata = extracted_data_factory()
    fake_extracted_data_repository.save(edata)
    return edata


@pytest.fixture
def extracted_data_service(application):
    return application.extracted_data()


@pytest.fixture()
def attachment_service_service_mock(containers, mocker):
    with containers.attachment_service.override(mocker.Mock(containers.attachment_service.cls)) as service:
        yield service()


@pytest.fixture
def perform_extraction_command_message(mocker, test_document_type):
    cm = mocker.Mock(CommandMessage)
    cm.command.document_id = str(random.randint(1, 10))
    cm.command.document_type_id = test_document_type.id()
    cm.command.tenant_id = test_document_type.tenant_id()
    cm.command.extra_data = {"template_version_id": uuid4().hex}
    cm.command.language = uuid4().hex
    cm.command.engine = uuid4().hex
    cm.message.headers = {"command_saga_id": uuid4().hex}
    cm.correlation_headers = {"test": "headers"}
    cm.command.llm_type = None

    return cm


@pytest.fixture(
    params=(
        raw_prototype_document_type,
        raw_plugin_document_type,
        raw_template_document_type,
        raw_document_type_without_extraction_type,
        #  add cloud native extractos
    ),
)
def raw_document_type(request):
    return request.param


@pytest.fixture
def raw_document_types():
    return [
        raw_prototype_document_type,
        raw_plugin_document_type,
        raw_template_document_type,
        raw_document_type_without_extraction_type,
    ]


@pytest.fixture
def messaging__raw_document_types(raw_document_types):
    messaging_raw_doc_types: list[RawDocumentType] = []  # type: ignore
    dt = raw_document_types[0]  # taking only the first one for optimization

    raw_document_types.append(
        {
            "document_type_id": dt["document_type_id"],
            "tenant_id": dt["tenant_id"],
            "name": dt["name"],
            "extraction_type": dt.get("extraction_type"),
            "fields": [
                {
                    "name": field.name,
                    "code": field.code,
                    "required": field.required,
                    "confidential": field.confidential,
                    "read_only": field.read_only,
                    "field_type": field.field_type,
                    "description": field.field_data.to_model() if field.field_data else None,
                    "order": field.order,
                }
                for field in [SerializedField(**field) for field in dt["fields"]]
            ],
        },
    )

    return messaging_raw_doc_types


@pytest.fixture
def get_document_types_reply_message(mocker, raw_document_types):
    cm = mocker.Mock(CommandMessage)
    cm.command = GetDocumentTypesReply(document_types=raw_document_types)

    return cm


def get_description_by_type(type_: str) -> dict[str, Any]:
    if type_ == FieldType.STRING:
        return StringFieldDescriptionFactory().to_dict()
    if type_ == FieldType.DICT:
        return DictFieldDescriptionFactory().to_dict()
    if type_ == FieldType.TABLE:
        return TableFieldDescriptionFactory().to_dict()
    if type_ == FieldType.LIST:
        return ListFieldDescriptionFactory().to_dict()
    if type_ == FieldType.ENUM:
        return EnumFieldDescriptionFactory().to_dict()
    if type_ == FieldType.DATE:
        return DateFieldDescriptionFactory().to_dict()


@pytest.fixture
def create_field_request() -> dict[str, Any]:
    type_ = random.choice(list(FieldType))
    return {
        "name": uuid4().hex,
        "type": type_,
        "required": random.choice((True, False)),
        "confidential": random.choice((True, False)),
        "read_only": random.choice((True, False)),
        "order": random.randint(0, 9),
        "description": get_description_by_type(type_),
    }


@pytest.fixture
def create_field_with_request_2() -> dict[str, Any]:
    type_ = random.choice(list(FieldType))
    return {
        "name": uuid4().hex,
        "type": type_,
        "required": random.choice((True, False)),
        "confidential": random.choice((True, False)),
        "read_only": random.choice((True, False)),
        "order": random.randint(0, 9),
        "description": get_description_by_type(type_),
    }


@pytest.fixture
def update_field_request() -> dict[str, Any]:
    return {
        "name": uuid4().hex,
        "required": random.choice((True, False)),
        "confidential": random.choice((True, False)),
        "read_only": random.choice((True, False)),
        "order": random.randint(0, 9),
    }


@pytest.fixture
def update_field_request_2() -> dict[str, Any]:  # rename
    return {
        "name": uuid4().hex,
        "required": random.choice((True, False)),
        "confidential": random.choice((True, False)),
        "read_only": random.choice((True, False)),
        "order": random.randint(0, 9),
    }


@pytest.fixture
def update_llm_params_request() -> dict[str, Any]:
    return {
        "custom_instruction": uuid4().hex,
        "grouping_factor": random.randint(1, 20),
        "temperature": random.random(),
    }


@pytest.fixture
def attach_extractor_request() -> dict[str, Any]:
    extractor_type = random.choice(list(ExtractorType))
    return {
        "name": uuid4().hex,
        "extractorType": extractor_type,
        "engine": uuid4().hex,
        "language": uuid4().hex,
        "imageTransformations": [uuid4().hex],
        "description": uuid4().hex,
    }


@pytest.fixture
def attachment_info() -> AttachmentInfo:
    return AttachmentInfo(command_channel=uuid4().hex, document_type_id=uuid4().hex, extractor_id=uuid4().hex)


@pytest.fixture
def attach_extractor_fields(create_field_request) -> list[FieldAttachment]:
    serialized_field = SerializedField(
        code="test_code",
        field_type=create_field_request.pop("type"),
        field_data=create_field_request.pop("description"),
        **create_field_request,
    )
    return [
        FieldAttachment(
            name=serialized_field.name,
            code=serialized_field.code,
            required=serialized_field.required,
            order=serialized_field.order,
            confidential=serialized_field.confidential,
            read_only=serialized_field.read_only,
            type=serialized_field.field_type,
            description=serialized_field.field_data.to_model() if serialized_field.field_data else None,
        )
    ]


@pytest.fixture
def attach_extractor_fields_2(create_field_with_request_2) -> list[FieldAttachment]:
    serialized_field = SerializedField(
        code="test_code",
        field_type=create_field_with_request_2.pop("type"),
        field_data=create_field_with_request_2.pop("description"),
        **create_field_with_request_2,
    )
    return [
        FieldAttachment(
            name=serialized_field.name,
            code=serialized_field.code,
            required=serialized_field.required,
            order=serialized_field.order,
            confidential=serialized_field.confidential,
            read_only=serialized_field.read_only,
            type=serialized_field.field_type,
            description=serialized_field.field_data.to_model() if serialized_field.field_data else None,
        )
    ]


@pytest.fixture
def attach_extractor_fields_without_orders(extraction_field_factory) -> list[FieldAttachment]:
    fields = extraction_field_factory.create_batch(10)
    return [
        FieldAttachment(
            name=field.name,
            code=field.code(),
            required=field.required,
            order=None,
            confidential=None,
            read_only=None,
            type=field.profile.type,
            description=field.profile.description,
        )
        for field in fields
    ]


@pytest.fixture
def attach_llm_extractor_fields_without_orders(extraction_field_factory) -> list[FieldAttachment]:
    fields = extraction_field_factory.create_batch(10)
    return [
        FieldAttachment(
            name=field.name,
            code=field.code(),
            required=field.required,
            order=None,
            confidential=None,
            read_only=None,
            type=field.profile.type,
            description=field.profile.description,
        )
        for field in fields
    ]


@pytest.fixture
def attached_extractor_info(
    test_tenant,
    attach_extractor_request,
    attach_extractor_fields_without_orders,
    attachment_service,
) -> AttachmentInfo:
    return attachment_service.attach_extractor(
        document_type_name="test_name",
        tenant_id=test_tenant,
        extractor_type=ExtractorType.PLUGIN,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_extractor_fields_without_orders,
    )


@pytest.fixture
def attached_llm_extractor_info(
    test_tenant,
    attach_extractor_request,
    attach_llm_extractor_fields_without_orders,
    attachment_service,
) -> AttachmentInfo:
    return attachment_service.attach_extractor(
        document_type_name="test_name",
        tenant_id=test_tenant,
        extractor_type=ExtractorType.LLM,
        description=attach_extractor_request["description"],
        engine=attach_extractor_request["engine"],
        language=attach_extractor_request["language"],
        image_transformations=attach_extractor_request["imageTransformations"],
        fields=attach_llm_extractor_fields_without_orders,
    )
