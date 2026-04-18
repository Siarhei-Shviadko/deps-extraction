from uuid import uuid4

import pytest
from deps_extracted_data import ExtractedFieldFactory


@pytest.fixture
def extracted_string_list_with_aliases_factory(
    ef_factory: ExtractedFieldFactory,
    extracted_string_factory_with_bbox_coord,
):
    elements = ([extracted_string_factory_with_bbox_coord().data, extracted_string_factory_with_bbox_coord().data],)
    return lambda: ef_factory.create_string_list(
        field_code=uuid4().hex,
        elements=elements,
        aliases={el.id: uuid4().hex for el in elements},
    )
