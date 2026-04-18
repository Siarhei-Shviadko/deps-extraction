import pytest

from deps_extraction.domain.dtos import ExtractedDataListFilterObject
from deps_extraction.domain.exceptions import ExtractedDataForbidden
from deps_extraction.infrastructure.data_object_accessors import TenantDAO
from deps_extraction.infrastructure.data_object_accessors.context_vars import user


@pytest.fixture
def database_connection(containers):
    db = containers.datasources.postgres_datasource()
    with db.connection() as conn:
        yield conn


class TestTenantDAO:
    document_id = 1
    tenant_dao = TenantDAO()

    def test_add_to_tenant__valid_data__successful(self, database_connection):
        self.tenant_dao.add_to_tenant(database_connection, self.document_id)
        tenant_documents = self.tenant_dao.get_document_ids(database_connection)

        self.tenant_dao.check_access(database_connection, self.document_id)
        assert len(tenant_documents) == 1
        assert tenant_documents[0] == self.document_id

    def test_add_to_tenant__user_has_only_his_data(self, other_organisation_user, database_connection):
        self.tenant_dao.add_to_tenant(database_connection, self.document_id)
        user.set(other_organisation_user)
        other_document_id = 123
        self.tenant_dao.add_to_tenant(database_connection, other_document_id)
        other_tenant_documents = self.tenant_dao.get_document_ids(database_connection)

        self.tenant_dao.check_access(database_connection, other_document_id)
        assert len(other_tenant_documents) == 1
        assert other_tenant_documents[0] == other_document_id

    def test_add_to_tenant_user_hasnt_access__raise_error(self, other_organisation_user, database_connection):
        self.tenant_dao.add_to_tenant(database_connection, self.document_id)

        user.set(other_organisation_user)
        with pytest.raises(ExtractedDataForbidden):
            self.tenant_dao.check_access(database_connection, self.document_id)

    def test_remove_from_tenant__user_lost_access(self, database_connection):
        self.tenant_dao.add_to_tenant(database_connection, self.document_id)
        self.tenant_dao.remove_from_tenant(database_connection, self.document_id)

        with pytest.raises(ExtractedDataForbidden):
            self.tenant_dao.check_access(database_connection, self.document_id)

    def test_check_access__access_exists__successful(self, database_connection):
        self.tenant_dao.add_to_tenant(database_connection, self.document_id)
        self.tenant_dao.check_access(database_connection, self.document_id)

    def test_check_access__access_denied__raise_error(self, database_connection):
        with pytest.raises(ExtractedDataForbidden):
            self.tenant_dao.check_access(database_connection, self.document_id)

    def test_patch_filter__filtering_doesnt_empty__return_intersection(self, database_connection):
        second_document_id = 144
        third_document_id = 456
        filtering = ExtractedDataListFilterObject(
            document_ids=[self.document_id, second_document_id, third_document_id]
        )
        self.tenant_dao.add_to_tenant(database_connection, self.document_id)
        self.tenant_dao.add_to_tenant(database_connection, second_document_id)
        self.tenant_dao.patch_filter(database_connection, filtering)

        assert len(filtering.document_ids) == 2
        assert third_document_id not in filtering.document_ids

    def test_patch_filter__filtering_is_empty__return_all_tenant_doc_ids(self, database_connection):
        for i in range(1, 4):
            self.tenant_dao.add_to_tenant(database_connection, i)
        filtering = ExtractedDataListFilterObject()
        self.tenant_dao.patch_filter(database_connection, filtering)

        assert len(filtering.document_ids) == 3

    def test_patch_filter__user_has_only_his_tenant_doc_ids(self, database_connection, other_organisation_user):
        self.tenant_dao.add_to_tenant(database_connection, self.document_id)
        user.set(other_organisation_user)
        other_document_id = 1000
        self.tenant_dao.add_to_tenant(database_connection, other_document_id)
        filtering = ExtractedDataListFilterObject(document_ids=[self.document_id, other_document_id])

        self.tenant_dao.patch_filter(database_connection, filtering)

        assert len(filtering.document_ids) == 1
        assert filtering.document_ids[0] == other_document_id
