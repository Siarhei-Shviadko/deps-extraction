from random import randint

import pytest

from deps_extraction.domain.exceptions import DocumentTypeNotFound
from deps_extraction.domain.model import DocumentType, Extractor, ExtractorType
from deps_extraction.infrastructure.repositories import DocumentTypeRepository


def compare_document_types(document_type1: DocumentType, document_type2: DocumentType) -> None:
    assert document_type1 == document_type2
    assert document_type1.tenant_id == document_type2.tenant_id
    assert document_type1.name == document_type2.name
    assert document_type1.extraction_fields == document_type2.extraction_fields

    assert document_type1.compliance_policies == document_type2.compliance_policies
    assert document_type1.extraction_type == document_type2.extraction_type
    assert len(document_type1.extractors) == len(document_type2.extractors)
    for extractor1, extractor2 in zip(document_type1.extractors.values(), document_type2.extractors.values()):
        compare_extractors(extractor1, extractor2)


def compare_extractors(extractor1: Extractor, extractor2: Extractor) -> None:
    assert extractor1 == extractor2
    assert extractor1.type == extractor2.type
    assert extractor1.fields == extractor2.fields
    assert extractor1.compliance_policies == extractor2.compliance_policies


@pytest.mark.document_type
def test_save__new_doc_type__successful(
    document_type_repository: DocumentTypeRepository,
    test_id: str,
    test_document_type: DocumentType,
):
    document_type_repository.save(test_document_type)

    saved_doc_type = document_type_repository.get(test_id)
    compare_document_types(saved_doc_type, test_document_type)


@pytest.mark.document_type
def test_save__new_doc_type_with_extractors__successful(
    document_type_repository: DocumentTypeRepository,
    test_id: str,
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
):
    document_type_repository.save(test_document_type_with_llm_and_plugin_extractors)

    saved_doc_type = document_type_repository.get(test_id)
    compare_document_types(saved_doc_type, test_document_type_with_llm_and_plugin_extractors)


@pytest.mark.document_type
def test_save__new_doc_type_with_extractors_and_fields__successful(
    document_type_repository: DocumentTypeRepository,
    test_id: str,
    test_document_type_with_llm_and_plugin_extractors_with_fields: DocumentType,
):
    document_type_repository.save(test_document_type_with_llm_and_plugin_extractors_with_fields)

    saved_doc_type = document_type_repository.get(test_id)
    compare_document_types(saved_doc_type, test_document_type_with_llm_and_plugin_extractors_with_fields)


@pytest.mark.document_type
def test_save_new__new_doc_type__successful(
    document_type_repository: DocumentTypeRepository,
    test_id: str,
    test_document_type: DocumentType,
    test_tenant: str,
):
    document_type_repository.save_new(test_document_type)

    saved_doc_type = document_type_repository.find_by_id_for_tenant(document_type_id=test_id, tenant_id=test_tenant)
    compare_document_types(saved_doc_type, test_document_type)


@pytest.mark.document_type
def test_save_new__new_doc_type_with_extractors__successful(
    document_type_repository: DocumentTypeRepository,
    test_id: str,
    test_document_type_with_llm_and_plugin_extractors: DocumentType,
    test_tenant: str,
):
    document_type_repository.save_new(test_document_type_with_llm_and_plugin_extractors)
    saved_doc_type = document_type_repository.find_by_id_for_tenant(document_type_id=test_id, tenant_id=test_tenant)
    compare_document_types(saved_doc_type, test_document_type_with_llm_and_plugin_extractors)


@pytest.mark.document_type
def test_find_by_id_for_tenant__no_doc_type__error(
    document_type_repository: DocumentTypeRepository, test_id: str, test_tenant: str
):
    with pytest.raises(DocumentTypeNotFound):
        document_type_repository.find_by_id_for_tenant(document_type_id=test_id, tenant_id=test_tenant)


@pytest.mark.document_type
def test_save__existing_doc_type__updated(
    document_type_repository: DocumentTypeRepository,
    document_type_factory,
    test_document_type: DocumentType,
    test_id: str,
):
    document_type_repository.save(test_document_type)
    document_type = document_type_factory(id_=test_document_type.id, tenant_id=test_document_type.tenant_id)

    document_type_repository.save(document_type)

    updated_doc_type = document_type_repository.get(test_id)
    compare_document_types(updated_doc_type, document_type)


@pytest.mark.document_type
def test_save__existing_doc_type_with_extractors__update_without_extractors__ok(
    document_type_repository: DocumentTypeRepository,
    document_type_factory,
    test_document_type_with_llm_extractors: DocumentType,
    test_id: str,
):
    document_type_repository.save(test_document_type_with_llm_extractors)
    document_type = document_type_factory(
        id_=test_document_type_with_llm_extractors.id,
        tenant_id=test_document_type_with_llm_extractors.tenant_id,
        extractors=[],
    )
    document_type_repository.save(document_type)

    updated_doc_type = document_type_repository.get(test_id)
    compare_document_types(updated_doc_type, document_type)


@pytest.mark.document_type
def test_save__existing_doc_type_with_extractors__update_extractor__ok(
    document_type_repository: DocumentTypeRepository,
    extractor_factory,
    test_document_type_with_llm_extractors: DocumentType,
    test_id: str,
):
    document_type_repository.save(test_document_type_with_llm_extractors)
    extractor = extractor_factory()
    test_document_type_with_llm_extractors.attach_extractor(
        type_=extractor.type,
        fields=[],
    )

    document_type_repository.save(test_document_type_with_llm_extractors)

    updated_doc_type = document_type_repository.get(test_id)
    compare_document_types(updated_doc_type, test_document_type_with_llm_extractors)


@pytest.mark.document_type
def test_save_new__existing_doc_type__not_updated(
    document_type_repository: DocumentTypeRepository,
    document_type_factory,
    test_document_type: DocumentType,
    test_id: str,
):
    document_type_repository.save_new(test_document_type)
    document_type = document_type_factory(id_=test_document_type.id, tenant_id=test_document_type.tenant_id)

    document_type_repository.save_new(document_type)

    saved_doc_type = document_type_repository.get(test_id)
    compare_document_types(saved_doc_type, test_document_type)


@pytest.mark.document_type
def test_save_all__no_doc_types__all_created(document_type_repository: DocumentTypeRepository, document_type_factory):
    document_type_batch_size = randint(10, 25)
    document_types = document_type_factory.create_batch(size=document_type_batch_size)

    document_type_repository.save_all(document_types)

    for document_type in document_types:
        saved_document_type = document_type_repository.get(document_type.id())

        compare_document_types(saved_document_type, document_type)


@pytest.mark.document_type
def test_save_all__empty_list__no_error(document_type_repository: DocumentTypeRepository, document_type_factory):
    document_type_repository.save_all([])


@pytest.mark.document_type
def test_save_new_all__no_doc_types__all_created(
    document_type_repository: DocumentTypeRepository, document_type_factory
):
    document_type_batch_size = randint(10, 25)
    document_types = document_type_factory.create_batch(size=document_type_batch_size)

    document_type_repository.save_new_all(document_types)

    for document_type in document_types:
        saved_document_type = document_type_repository.get(document_type.id())

        compare_document_types(saved_document_type, document_type)


@pytest.mark.document_type
def test_save_all__doc_types_exist__all_updated(
    document_type_repository: DocumentTypeRepository, document_type_factory
):
    document_type_batch_size = randint(10, 25)
    document_types = document_type_factory.create_batch(size=document_type_batch_size)
    document_type_repository.save_all(document_types)
    updated_document_types = [
        document_type_factory(id_=document_type.id, tenant_id=document_type.tenant_id)
        for document_type in document_types
    ]

    document_type_repository.save_all(updated_document_types)

    for document_type in updated_document_types:
        updated_document_type = document_type_repository.get(document_type.id())

        compare_document_types(updated_document_type, document_type)


@pytest.mark.document_type
def test_save_new_all__doc_types_exist__all_not_updated(
    document_type_repository: DocumentTypeRepository, document_type_factory
):
    document_type_batch_size = randint(10, 25)
    document_types = document_type_factory.create_batch(size=document_type_batch_size)
    document_type_repository.save_new_all(document_types)
    updated_document_types = [
        document_type_factory(id_=document_type.id, tenant_id=document_type.tenant_id)
        for document_type in document_types
    ]

    document_type_repository.save_new_all(updated_document_types)

    for document_type in document_types:
        saved_document_type = document_type_repository.get(document_type.id())

        compare_document_types(saved_document_type, document_type)


@pytest.mark.document_type
def test_save_new_all__empty_list__no_error(document_type_repository: DocumentTypeRepository, document_type_factory):
    document_type_repository.save_new_all([])


@pytest.mark.document_type
def test_delete__doc_type_exists__deleted(
    document_type_repository: DocumentTypeRepository, test_id: str, test_document_type: DocumentType
):
    document_type_repository.save(test_document_type)
    assert document_type_repository.get(test_id)

    document_type_repository.delete(test_document_type)

    assert not document_type_repository.get(test_id)


@pytest.mark.document_type
def test_delete__no_doc_type__no_error(
    document_type_repository: DocumentTypeRepository, test_id: str, test_document_type: DocumentType
):
    document_type_repository.delete(test_document_type)


@pytest.mark.document_type
def test_find_by_tenant__no_doc_type__empty(document_type_repository: DocumentTypeRepository, test_tenant: str):
    document_types = document_type_repository.find_by_tenant(tenant_id=test_tenant)

    assert len(document_types) == 0


def test_find_by_tenant__no_doc_type__not_empty(
    document_type_repository: DocumentTypeRepository, test_tenant: str, test_document_type: DocumentType
):
    document_type_repository.save(test_document_type)

    document_types = document_type_repository.find_by_tenant(tenant_id=test_tenant)

    assert len(document_types) == 1
    assert isinstance(document_types[0], DocumentType)


def test_find_by_name_for_tenant__no_doc_type__empty(
    document_type_repository: DocumentTypeRepository,
    test_tenant: str,
):
    document_type = document_type_repository.find_by_name_for_tenant(
        document_type_name="test name", tenant_id=test_tenant
    )

    assert document_type is None


def test_find_by_name_for_tenant__doc_type_exist__not_empty(
    document_type_repository: DocumentTypeRepository,
    test_document_type: DocumentType,
    test_tenant: str,
):
    document_type_repository.save(test_document_type)
    document_type = document_type_repository.find_by_name_for_tenant(
        document_type_name=test_document_type.name, tenant_id=test_tenant
    )

    assert document_type == test_document_type


def test_find_by_name_for_tenant__other_tenant__empty(
    document_type_repository: DocumentTypeRepository,
    test_document_type: DocumentType,
    test_tenant: str,
):
    document_type_repository.save(test_document_type)
    document_type = document_type_repository.find_by_name_for_tenant(
        document_type_name=test_document_type.name,
        tenant_id="different",
    )

    assert document_type is None


def test_find_all_document_types(document_type_repository, document_type_factory):
    document_types = sorted([document_type_factory(extractor_size=2) for _ in range(10)], key=lambda dt: dt.id())
    document_type_repository.save_all(document_types)

    saved_document_types = sorted(document_type_repository.find_all(), key=lambda dt: dt.id())

    assert saved_document_types == document_types
