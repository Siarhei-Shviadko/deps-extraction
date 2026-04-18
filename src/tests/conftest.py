import random
from copy import deepcopy
from typing import Any

from fastapi import FastAPI
from pytest_factoryboy import register
from starlette.testclient import TestClient

from deps_extraction import api
from deps_extraction.domain.model import (
    DocumentType,
    DocumentTypeFactory,
    ExtractionType,
    ExtractionWorkflow,
    ExtractionWorkflowBuilder,
    ExtractorType,
)
from deps_extraction.entrypoint import create_fastapi
from deps_extraction.infrastructure.data_object_accessors.context_vars import user
from tests.data import create_field_payload, create_field_payload_2
from tests.extracted_data_fixtures import *
from tests.factories import (
    BboxFactory,
    CellCoordinatesFactory,
    CellRangeFactory,
    CharRangeFactory,
)
from tests.factories import DocumentTypeFactory as FactoryBoyDocumentTypeFactory
from tests.factories import (
    ExtractionFieldFactory,
    ExtractorFactory,
    GroupFactory,
    SourceBboxCoordinatesFactory,
    SourceTableCoordinatesFactory,
    SourceTextCoordinatesFactory,
    StringDataFactory,
    TableMetaFactory,
    TableRowFactory,
)

FIRST_ELEMENT = 0


@pytest.fixture(scope="session")
def app() -> FastAPI:
    fastapi_app = create_fastapi()
    yield fastapi_app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def containers(app):
    return app.containers


@pytest.fixture
def repositories(containers):
    return containers.repositories


@pytest.fixture
def application(containers):
    return containers.application()


@pytest.fixture
def messaging(containers):
    return containers.messaging


@pytest.fixture
def test_id():
    return uuid4().hex


@pytest.fixture
def test_tenant():
    return uuid4().hex


@pytest.fixture
def document_type_name():
    return uuid4().hex


@pytest.fixture
def test_document_type(test_id, test_tenant, document_type_name):
    return DocumentTypeFactory.create(id_=test_id, tenant_id=test_tenant, name=document_type_name)


@pytest.fixture
def test_document_type_with_llm_extractors(test_id, test_tenant, document_type_name):
    doc_type = DocumentTypeFactory.create(
        id_=test_id,
        tenant_id=test_tenant,
        name=document_type_name,
        extraction_type=ExtractionType.NON,
    )
    doc_type.attach_extractor(type_=ExtractorType.LLM, fields=[])
    doc_type.events.clear()
    return doc_type


@pytest.fixture
def test_document_type_with_plugin_extractor(test_id, test_tenant, document_type_name):
    doc_type = DocumentTypeFactory.create(
        id_=test_id,
        tenant_id=test_tenant,
        name=document_type_name,
        extraction_type=ExtractionType.NON,
    )
    doc_type.attach_extractor(type_=ExtractorType.PLUGIN, fields=[])
    doc_type.events.clear()
    return doc_type


@pytest.fixture
def test_document_type_with_llm_and_plugin_extractors(test_id, test_tenant, document_type_name):
    doc_type = DocumentTypeFactory.create(
        id_=test_id,
        tenant_id=test_tenant,
        name=document_type_name,
        extraction_type=ExtractionType.NON,
    )
    doc_type.attach_extractor(type_=ExtractorType.LLM, fields=[])
    doc_type.attach_extractor(type_=ExtractorType.PLUGIN, fields=[])
    doc_type.events.clear()
    return doc_type


@pytest.fixture
def test_document_type_with_2_llm_and_plugin_extractors(test_id, test_tenant, document_type_name):
    doc_type = DocumentTypeFactory.create(
        id_=test_id,
        tenant_id=test_tenant,
        name=document_type_name,
        extraction_type=ExtractionType.NON,
    )
    doc_type.attach_extractor(type_=ExtractorType.LLM, fields=[])
    doc_type.attach_extractor(type_=ExtractorType.LLM, fields=[])
    doc_type.attach_extractor(type_=ExtractorType.PLUGIN, fields=[])
    doc_type.events.clear()
    return doc_type


@pytest.fixture
def test_document_type_with_template_extractors(test_id, test_tenant, document_type_name):
    doc_type = DocumentTypeFactory.create(
        id_=test_id,
        tenant_id=test_tenant,
        name=document_type_name,
        extraction_type=ExtractionType.TEMPLATE,
    )
    doc_type.events.clear()
    return doc_type


@pytest.fixture
def test_document_type_with_prototype_extractors(test_id, test_tenant, document_type_name):
    doc_type = DocumentTypeFactory.create(
        id_=test_id,
        tenant_id=test_tenant,
        name=document_type_name,
        extraction_type=ExtractionType.PROTOTYPE,
    )
    doc_type.events.clear()
    return doc_type


@pytest.fixture
def test_document_type_with_template_extractors_and_fields(test_id, test_tenant, document_type_name):
    doc_type = DocumentTypeFactory.create(
        id_=test_id,
        tenant_id=test_tenant,
        name=document_type_name,
        extraction_type=ExtractionType.TEMPLATE,
    )
    doc_type.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
    )
    doc_type.events.clear()
    return doc_type


@pytest.fixture
def test_document_type_with_template_and_llm_extractors(test_id, test_tenant, document_type_name):
    doc_type = DocumentTypeFactory.create(
        id_=test_id,
        tenant_id=test_tenant,
        name=document_type_name,
        extraction_type=ExtractionType.TEMPLATE,
    )
    doc_type.attach_extractor(type_=ExtractorType.LLM, fields=[])
    doc_type.events.clear()
    return doc_type


@pytest.fixture
def test_document_type_with_llm_and_plugin_extractors_with_fields(
    test_document_type_with_llm_and_plugin_extractors,
):
    test_document_type_with_llm_and_plugin_extractors.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
    )
    llm_extractor_id = next(
        (
            e
            for e in test_document_type_with_llm_and_plugin_extractors.extractors.values()
            if e.type == ExtractorType.LLM
        )
    ).id()
    test_document_type_with_llm_and_plugin_extractors.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
        extractor_id=llm_extractor_id,
    )
    test_document_type_with_llm_and_plugin_extractors.events.clear()
    return test_document_type_with_llm_and_plugin_extractors


@pytest.fixture
def test_document_type_plugin_extractor_with_field(test_document_type_with_plugin_extractor):
    test_document_type_with_plugin_extractor.add_field(
        name=create_field_payload["name"],
        type_=create_field_payload["type"],
        required=create_field_payload["required"],
    )
    test_document_type_with_plugin_extractor.events.clear()

    return test_document_type_with_plugin_extractor


@pytest.fixture
def test_document_type_llm_extractor_with_field(test_document_type_with_llm_extractors):
    llm_extractor = next(
        (
            extractor
            for extractor in test_document_type_with_llm_extractors.extractors.values()
            if extractor.type == ExtractorType.LLM
        )
    )
    test_document_type_with_llm_extractors.add_field(
        name=create_field_payload_2["name"],
        type_=create_field_payload_2["type"],
        required=create_field_payload_2["required"],
        extractor_id=llm_extractor.id(),
    )
    test_document_type_with_llm_extractors.events.clear()

    return test_document_type_with_llm_extractors


@pytest.fixture
def test_correlation_headers() -> dict[str, str]:
    return {
        "commandreply_saga_type": "DocumentProcessingSaga",
        "commandreply_saga_id": uuid4().hex,
        "commandreply_destination": "ExtractionService",
        "commandreply_type": "PerformExtraction",
        "commandreply_reply_to": "DocumentProcessingSaga-reply",
        "reply_to_message_id": uuid4().hex,
    }


@pytest.fixture
def test_extra_headers(this_user) -> dict[str, Any]:
    return {
        "ID": uuid4().hex,
        "RabbitMQMessageID": uuid4().hex,
        "command_destination": "ExtractionService",
        "command_reply_to": "DocumentProcessingSaga-reply",
        "command_saga_id": "c17889bfa60d455f939a57b824520537",
        "command_saga_type": "DocumentProcessingSaga",
        "command_type": "PerformExtraction",
        "x-user-creds": {
            "deps_token": "token",
            "email": this_user.get("email"),
            "first_name": this_user.get("first_name"),
            "groups": this_user["groups"],
            "last_name": this_user.get("last_name"),
            "organisation": this_user["organisation"],
            "roles": this_user["roles"],
            "subject": this_user["subject"],
        },
    }


@pytest.fixture
def perform_extraction_payload(test_correlation_headers, test_tenant, test_extra_headers):
    return {
        "document_id": str(random.randint(1, 10000)),
        "tenant_id": test_tenant,
        "correlation_headers": test_correlation_headers,
        "template_version_id": uuid4().hex,
        "language": random.choice(("eng", "rus", "jap")),
        "engine": random.choice(("TESSERACT", "AZURE_FORM_RECOGNIZER", "AWS_TEXTRACT")),
        "extra_headers": test_extra_headers,
        "llm_type": random.choice(("gpt-4", "gemini 2.5")),
    }


@pytest.fixture
def test_extraction_workflow_with_steps(
    test_tenant, test_correlation_headers, test_extra_headers
) -> ExtractionWorkflow:
    builder = ExtractionWorkflowBuilder(
        document_id=uuid4().hex,
        tenant_id=test_tenant,
        document_type_id=uuid4().hex,
        command_channel=uuid4().hex,
        correlation_headers=test_correlation_headers,
        extra_headers=test_extra_headers,
        template_version_id=uuid4().hex,
        language=random.choice(("eng", "rus", "jap")),
        engine=random.choice(("TESSERACT", "AZURE_FORM_RECOGNIZER", "AWS_TEXTRACT")),
        llm_type=random.choice(("gpt-4", "gemini 2.5")),
    )
    for extractor_id, extractor_type in zip(
        (uuid4().hex, uuid4().hex, uuid4().hex), (ExtractorType.LLM, ExtractorType.LLM, ExtractorType.PLUGIN)
    ):
        builder.with_step_for(extractor_id=extractor_id, extractor_type=extractor_type)
    return builder.build()


@pytest.fixture
def test_field(test_document_type_plugin_extractor_with_field: DocumentType):
    return test_document_type_plugin_extractor_with_field.extraction_fields[FIRST_ELEMENT]


@pytest.fixture
def config(containers):
    return containers.config


@pytest.fixture
def this_user(test_tenant):
    return dict(
        subject="PinkKey",
        groups=[test_tenant],
        token="token",
        roles=["doctor"],
        organisation=test_tenant,
    )


@pytest.fixture
def other_organisation_user():
    return dict(subject="TestKey", groups=["OtherORG"], token="fakenToken", roles=["testRole"], organisation="OtherORG")


@pytest.fixture(autouse=True)
def set_this_user(this_user):
    user.set(this_user)


@pytest.fixture(autouse=True)
def mocked_middleware(monkeypatch, mocker):
    monkeypatch.setattr(api.auth, "set_user_from_token", mocker.Mock({}))


register(BboxFactory)
register(CellCoordinatesFactory)
register(SourceBboxCoordinatesFactory)
register(SourceTableCoordinatesFactory)
register(SourceTextCoordinatesFactory)
register(CharRangeFactory)
register(CellRangeFactory)
register(StringDataFactory)
register(TableRowFactory)
register(TableMetaFactory)
register(GroupFactory)
register(ExtractionFieldFactory)
register(FactoryBoyDocumentTypeFactory)
register(ExtractorFactory)
