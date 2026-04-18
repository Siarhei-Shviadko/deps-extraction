import copy

import pytest
from deps_extracted_data import FieldType
from deps_extracted_data.model.extracted_data import ExtractedDataFactory

from deps_extraction.domain.dtos import (
    ExtractedDataFilterObject,
    ExtractedDataListFilterObject,
)
from deps_extraction.domain.exceptions import (
    ExtractedDataForbidden,
    ExtractedDataNotFound,
)
from deps_extraction.infrastructure.data_object_accessors.context_vars import user
from tests.data.chunked_data import (
    cells_row1,
    cells_row2,
    cells_row3,
    cells_row4,
    cells_row5,
    cells_row6,
)

FAKE_DOC_ID: int = 0


class TestExtractedDataRepository:
    def test_save__edata_not_exists__saved(self, extracted_data_factory, extracted_data_repository):
        edata = extracted_data_factory()
        extracted_data_repository.save(edata)
        res = extracted_data_repository.find(edata.document_id)
        assert res == edata

    def test_save__edata_exists__updated(self, extracted_data_factory, extracted_data_repository):
        edata1 = extracted_data_factory()
        edata2 = extracted_data_factory(external_doc_id=edata1.document_id)
        extracted_data_repository.save(edata1)
        extracted_data_repository.save(edata2)
        res = extracted_data_repository.find(edata2.document_id)

        assert edata1.document_id == edata2.document_id
        assert edata1 != edata2
        assert res == edata2

    def test_save__edata_belong_to_other_user__raise_error(
        self, extracted_data_factory, extracted_data_repository, other_organisation_user
    ):
        edata1 = extracted_data_factory()
        edata2 = extracted_data_factory(external_doc_id=edata1.document_id)
        extracted_data_repository.save(edata1)
        user.set(other_organisation_user)
        with pytest.raises(ExtractedDataForbidden):
            extracted_data_repository.save(edata2)

    def test_save__empty_extracted_data__edata_not_found(
        self, extracted_data_factory, extracted_data_repository, empty_extracted_data
    ):
        full_edata = extracted_data_factory(external_doc_id=empty_extracted_data.document_id)
        extracted_data_repository.save(full_edata)
        extracted_data_repository.save(empty_extracted_data)

        with pytest.raises(ExtractedDataNotFound):
            extracted_data_repository.find(empty_extracted_data.document_id)

    def test_find__edata_doesnt_exist__edata_not_found(self, extracted_data_repository):
        with pytest.raises(ExtractedDataNotFound):
            extracted_data_repository.find(FAKE_DOC_ID)

    def test_find_by_filter__by_field_code__correctly(self, extracted_data_repository, extracted_data_factory):
        edata = extracted_data_repository.save(extracted_data_factory())
        filtering = ExtractedDataFilterObject(document_id=edata.document_id, field_codes=[edata.fields[0].field_code])
        res = extracted_data_repository.find_by_filter(filtering)

        assert len(res.fields) == 1
        assert res.fields[0].field_code == edata.fields[0].field_code

    def test_find_by_filter__by_field_types__correctly(self, extracted_data_repository, extracted_data_factory):
        edata = extracted_data_repository.save(extracted_data_factory())
        filtering = ExtractedDataFilterObject(
            document_id=edata.document_id,
            field_types=[
                FieldType.STRING.value,
                FieldType.KEY_VALUE_PAIR_LIST.value,
            ],
        )
        res = extracted_data_repository.find_by_filter(filtering)

        assert len(res.fields) == 5
        assert len(res.string_fields) == 3
        assert len(res.key_value_pair_list_fields) == 2

    def test_find_by_filter__edata_doesnt_exist__forbidden_error(self, extracted_data_repository):
        with pytest.raises(ExtractedDataNotFound):
            extracted_data_repository.find_by_filter(ExtractedDataFilterObject(document_id=FAKE_DOC_ID))

    def test_find_by_filter__edata_belong_other_user__forbidden_error(
        self, extracted_data_repository, extracted_data_factory, other_organisation_user
    ):
        edata1 = extracted_data_factory()
        extracted_data_repository.save(edata1)
        user.set(other_organisation_user)
        filtering = ExtractedDataFilterObject(document_id=edata1.document_id)
        with pytest.raises(ExtractedDataNotFound):
            extracted_data_repository.find_by_filter(filtering)

    def test_delete__edata_exists__deleted(self, extracted_data_factory, extracted_data_repository):
        edata = extracted_data_repository.save(extracted_data_factory())
        extracted_data_repository.find(edata.document_id)
        extracted_data_repository.delete(edata.document_id)

        with pytest.raises(ExtractedDataNotFound):
            extracted_data_repository.find(edata.document_id)

    def test_delete__edata_doesnt_exist__no_error(self, extracted_data_repository):
        extracted_data_repository.delete(FAKE_DOC_ID)

    def test_delete__edata_belog_to_other_tenant__raise_forbidden(
        self, extracted_data_factory, extracted_data_repository, other_organisation_user, this_user
    ):
        edata = extracted_data_repository.save(extracted_data_factory())
        user.set(other_organisation_user)

        with pytest.raises(ExtractedDataForbidden):
            extracted_data_repository.delete(edata.document_id)

    def test_find_list_by_filter__with_one_doc_id__got_one(self, extracted_data_factory, extracted_data_repository):
        extracted_data_repository.save(extracted_data_factory(external_doc_id=1))
        edata2 = extracted_data_repository.save(extracted_data_factory(external_doc_id=2))

        filtering = ExtractedDataListFilterObject(document_ids=[edata2.document_id])
        edatas = extracted_data_repository.find_list_by_filter(filtering)

        assert edatas == [edata2]

    def test_find_list_by_filter__with_two_doc_ids__got_all(self, extracted_data_factory, extracted_data_repository):
        edata1 = extracted_data_repository.save(extracted_data_factory(external_doc_id=1))
        edata2 = extracted_data_repository.save(extracted_data_factory(external_doc_id=2))

        filtering = ExtractedDataListFilterObject(document_ids=[edata1.document_id, edata2.document_id])
        edatas = extracted_data_repository.find_list_by_filter(filtering)

        assert edatas == [edata1, edata2]

    def test_find_list_by_filter__empty_filtering__got_all(self, extracted_data_factory, extracted_data_repository):
        edata1 = extracted_data_repository.save(extracted_data_factory(external_doc_id=1))
        edata2 = extracted_data_repository.save(extracted_data_factory(external_doc_id=2))
        edata3 = extracted_data_repository.save(extracted_data_factory(external_doc_id=3))

        filtering = ExtractedDataListFilterObject()
        edatas = extracted_data_repository.find_list_by_filter(filtering)

        assert edatas == [edata1, edata2, edata3]

    def test_find_list_by_filter__edata_doesnt_exists__empty_list(self, extracted_data_repository):
        filtering = ExtractedDataListFilterObject()
        edatas = extracted_data_repository.find_list_by_filter(filtering)

        assert edatas == []

    def test_find_list_by_filter__edata_belong_to_other_tenant__return_empty_list(
        self, extracted_data_factory, extracted_data_repository, other_organisation_user
    ):
        edata = extracted_data_repository.save(extracted_data_factory(external_doc_id=1))
        user.set(other_organisation_user)

        filtering = ExtractedDataListFilterObject(document_ids=[edata.document_id])
        edatas = extracted_data_repository.find_list_by_filter(filtering)

        assert edatas == []

    def test_find_list_by_filter__edata_belong_to_other_tenant__return_only_own_edata(
        self, extracted_data_factory, extracted_data_repository, other_organisation_user
    ):
        edata1 = extracted_data_repository.save(extracted_data_factory(external_doc_id=1))
        user.set(other_organisation_user)
        edata2 = extracted_data_repository.save(extracted_data_factory(external_doc_id=2))
        filtering = ExtractedDataListFilterObject(document_ids=[edata1.document_id, edata2.document_id])
        edatas = extracted_data_repository.find_list_by_filter(filtering)

        assert len(edatas) == 1
        assert edatas[0] == edata2

    def test_find_list_by_filter__limit_and_offset__correctly(self, extracted_data_factory, extracted_data_repository):
        edata1 = extracted_data_repository.save(extracted_data_factory(external_doc_id=1))
        edata2 = extracted_data_repository.save(extracted_data_factory(external_doc_id=2))
        edata3 = extracted_data_repository.save(extracted_data_factory(external_doc_id=3))

        filtering = ExtractedDataListFilterObject()
        edatas = extracted_data_repository.find_list_by_filter(filtering)
        assert len(edatas) == 3
        assert edatas == [edata1, edata2, edata3]

        filtering.limit = 1
        filtering.document_ids = []
        limited_edatas = extracted_data_repository.find_list_by_filter(filtering)
        assert len(limited_edatas) == 1
        assert limited_edatas == [edata1]

        filtering.limit = None
        filtering.offset = 1
        filtering.document_ids = []
        offset_edatas = extracted_data_repository.find_list_by_filter(filtering)
        assert len(offset_edatas) == 2
        assert offset_edatas == [edata2, edata3]

    def test_find_list_by_filter__document_pks__correctly(self, extracted_data_factory, extracted_data_repository):
        edata1 = extracted_data_factory(external_doc_id=1)
        edata2 = extracted_data_factory(external_doc_id=2)
        extracted_data_repository.save(edata1)
        extracted_data_repository.save(edata2)

        filtering = ExtractedDataListFilterObject()
        edatas = extracted_data_repository.find_list_by_filter(filtering)
        assert len(edatas) == 2
        assert edatas == [edata1, edata2]

        filtering.document_ids = [edata1.document_id]
        edatas = extracted_data_repository.find_list_by_filter(filtering)
        assert edatas == [edata1]

        filtering.document_ids = [edata2.document_id]
        edatas = extracted_data_repository.find_list_by_filter(filtering)
        assert edatas == [edata2]

    @pytest.mark.parametrize("pagination", [(1, 6), (2, 3), (3, 2)])
    def test_find_with_internal_pagination__successful(
        self,
        pagination,
        extracted_data_repository,
        extracted_table_factory_from_dict,
    ):
        rows_per_chunk, expected_chunks = pagination
        doc_id = 1
        rows = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        cells = cells_row1 + cells_row2 + cells_row3 + cells_row4 + cells_row5 + cells_row6
        table_field = extracted_table_factory_from_dict(rows=rows, cells=copy.deepcopy(cells))
        edata = ExtractedDataFactory().make_extracted_data(doc_id)
        edata.add_table(table_field)
        extracted_data_repository.save(edata)

        result = extracted_data_repository.find_with_internal_pagination(doc_id, rows_per_chunk)
        assert result.table_fields[0].data.cells == []
        assert result.table_fields[0].data.meta.chunks_total == expected_chunks
        assert result.table_fields[0].data.meta.rows_total == len(rows)

    def test_find_with_internal_pagination__no_edata__error(self, extracted_data_repository):
        with pytest.raises(ExtractedDataNotFound):
            extracted_data_repository.find_with_internal_pagination(111, 1)

    @pytest.mark.aliases
    @pytest.mark.parametrize(
        "edata_method, field_factory",
        [
            ("add_string_list", "extracted_string_list_factory"),
            ("add_key_value_pair_list", "extracted_key_value_pair_list_factory"),
            ("add_table_list", "extracted_table_list_factory"),
            ("add_checkbox_list", "extracted_checkbox_list_factory"),
        ],
    )
    def test_save_extracted_data_with_aliases(
        self, edata_method, field_factory, request, extracted_data_repository, empty_extracted_data
    ):
        factory = request.getfixturevalue(field_factory)
        getattr(empty_extracted_data, edata_method)(factory(with_aliases=True))
        getattr(empty_extracted_data, edata_method)(factory())

        extracted_data_repository.save(empty_extracted_data)

        saved_edata = extracted_data_repository.find(empty_extracted_data.document_id)

        assert empty_extracted_data == saved_edata
