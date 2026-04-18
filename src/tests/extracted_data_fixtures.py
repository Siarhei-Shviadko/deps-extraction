from collections import defaultdict
from random import choice, randint, uniform
from uuid import uuid4

import pytest
from deps_extracted_data import (
    Bbox,
    CellCoordinates,
    CellRange,
    CharRange,
    CheckboxValue,
    EntityId,
    ExtractedDataFactory,
    ExtractedFieldFactory,
    FieldDataFactory,
    SourceBboxCoordinates,
    SourceTableCoordinates,
    SourceTextCoordinates,
    TableCellCoordinates,
    TableMeta,
)


@pytest.fixture
def float_coordinates():
    return uniform(0.0, 0.7), uniform(0.0, 0.7), uniform(0.0, 0.2), uniform(0.0, 0.2)


@pytest.fixture
def bbox_factory(float_coordinates):
    return lambda: Bbox(*float_coordinates)


@pytest.fixture
def source_id():
    return uuid4().hex


@pytest.fixture
def source_bbox_coordinates_factory(source_id, bbox_factory):
    return lambda: SourceBboxCoordinates(source_id, [bbox_factory(), bbox_factory()])


@pytest.fixture
def int_coordinates():
    a = randint(0, 100)
    return a, randint(a, 100)


@pytest.fixture
def entity_id_factory():
    return lambda: EntityId()


@pytest.fixture
def table_cell_coordinates(int_coordinates):
    return TableCellCoordinates(column=int_coordinates[0], row=int_coordinates[1], column_span=1, row_span=1)


@pytest.fixture
def cell_coordinates_factory(int_coordinates):
    return lambda: CellCoordinates(*int_coordinates)


@pytest.fixture
def cell_range_factory(cell_coordinates_factory):
    return lambda: CellRange.with_end(cell_coordinates_factory(), cell_coordinates_factory())


@pytest.fixture
def source_table_coordinates_factory(source_id, cell_range_factory):
    return lambda: SourceTableCoordinates(source_id, [cell_range_factory(), cell_range_factory()])


@pytest.fixture
def char_range_factory(int_coordinates):
    return lambda: CharRange(*int_coordinates)


@pytest.fixture
def source_text_coordinates_factory(source_id, char_range_factory):
    return lambda: SourceTextCoordinates(source_id, [char_range_factory(), char_range_factory()])


@pytest.fixture
def value():
    return uuid4().hex


@pytest.fixture
def checkbox_value():
    return CheckboxValue.CHECKED


@pytest.fixture
def confidence():
    return uniform(0.0, 1.0)


@pytest.fixture
def fd_factory():
    return FieldDataFactory()


@pytest.fixture
def field_code_factory():
    return lambda: uuid4().hex


@pytest.fixture
def ef_factory():
    return ExtractedFieldFactory()


@pytest.fixture
def table_cell_coordinates_factory():
    counter = defaultdict(int)

    def _factory() -> TableCellCoordinates:
        n = counter["calls"]
        counter["calls"] += 1
        col = n % 2
        row = (n // 2) % 2
        return TableCellCoordinates(column=col, row=row, column_span=1, row_span=1)

    return _factory


@pytest.fixture
def extracted_string_factory_with_bbox_coord(ef_factory: ExtractedFieldFactory, source_bbox_coordinates_factory):
    return lambda: ef_factory.create_string(
        uuid4().hex,
        uuid4().hex,
        [source_bbox_coordinates_factory(), source_bbox_coordinates_factory()],
        uniform(0.1, 0.9),
    )


@pytest.fixture
def extracted_string_factory_with_table_coord(ef_factory: ExtractedFieldFactory, source_table_coordinates_factory):
    return lambda: ef_factory.create_string(
        uuid4().hex,
        uuid4().hex,
        [source_table_coordinates_factory(), source_table_coordinates_factory()],
        uniform(0.1, 0.9),
    )


@pytest.fixture
def extracted_string_factory_with_text_coord(ef_factory: ExtractedFieldFactory, source_text_coordinates_factory):
    return lambda: ef_factory.create_string(
        uuid4().hex,
        uuid4().hex,
        [source_text_coordinates_factory(), source_text_coordinates_factory()],
        uniform(0.1, 0.9),
    )


def generate_checkbox_value():
    return choice(list(CheckboxValue))


@pytest.fixture
def extracted_checkbox_factory_with_bbox_coord(ef_factory: ExtractedFieldFactory, source_bbox_coordinates_factory):
    return lambda: ef_factory.create_checkbox(
        uuid4().hex,
        generate_checkbox_value(),
        [source_bbox_coordinates_factory(), source_bbox_coordinates_factory()],
        uniform(0.1, 0.9),
    )


@pytest.fixture
def extracted_checkbox_factory_with_table_coord(ef_factory: ExtractedFieldFactory, source_table_coordinates_factory):
    return lambda: ef_factory.create_checkbox(
        uuid4().hex,
        generate_checkbox_value(),
        [source_table_coordinates_factory(), source_table_coordinates_factory()],
        uniform(0.1, 0.9),
    )


@pytest.fixture
def extracted_checkbox_factory_with_text_coord(ef_factory: ExtractedFieldFactory, source_text_coordinates_factory):
    return lambda: ef_factory.create_checkbox(
        uuid4().hex,
        generate_checkbox_value(),
        [source_text_coordinates_factory(), source_text_coordinates_factory()],
        uniform(0.1, 0.9),
    )


@pytest.fixture
def extracted_key_value_pair_factory_with_bbox_coord(
    ef_factory: ExtractedFieldFactory,
    fd_factory: FieldDataFactory,
    source_bbox_coordinates_factory,
):
    return lambda: ef_factory.create_key_value_pair(
        uuid4().hex,
        fd_factory.create_string(
            uuid4().hex,
            [source_bbox_coordinates_factory(), source_bbox_coordinates_factory()],
            uniform(0.1, 0.9),
        ),
        fd_factory.create_checkbox(
            generate_checkbox_value(),
            [source_bbox_coordinates_factory(), source_bbox_coordinates_factory()],
            uniform(0.1, 0.9),
        ),
    )


@pytest.fixture
def extracted_key_value_pair_factory_with_table_coord(
    ef_factory: ExtractedFieldFactory,
    fd_factory: FieldDataFactory,
    source_table_coordinates_factory,
):
    return lambda: ef_factory.create_key_value_pair(
        uuid4().hex,
        fd_factory.create_string(
            uuid4().hex,
            [source_table_coordinates_factory(), source_table_coordinates_factory()],
            uniform(0.1, 0.9),
        ),
        fd_factory.create_checkbox(
            generate_checkbox_value(),
            [source_table_coordinates_factory(), source_table_coordinates_factory()],
            uniform(0.1, 0.9),
        ),
    )


@pytest.fixture
def extracted_key_value_pair_factory_with_text_coord(
    ef_factory: ExtractedFieldFactory,
    fd_factory: FieldDataFactory,
    source_text_coordinates_factory,
):
    return lambda: ef_factory.create_key_value_pair(
        uuid4().hex,
        fd_factory.create_string(
            uuid4().hex,
            [source_text_coordinates_factory(), source_text_coordinates_factory()],
            uniform(0.1, 0.9),
        ),
        fd_factory.create_checkbox(
            generate_checkbox_value(),
            [source_text_coordinates_factory(), source_text_coordinates_factory()],
            uniform(0.1, 0.9),
        ),
    )


@pytest.fixture
def table_meta():
    return TableMeta(
        chunks_total=randint(1, 40),
        rows_total=randint(1, 40),
        list_index=randint(1, 40),
    )


@pytest.fixture
def extracted_table_factory_with_bbox_coord(
    ef_factory: ExtractedFieldFactory,
    source_bbox_coordinates_factory,
    table_meta,
    table_cell_coordinates_factory,
    entity_id_factory,
):
    return lambda: ef_factory.create_table(
        uuid4().hex,
        sorted([uniform(0.1, 0.4), uniform(0.6, 0.9)]),
        sorted([uniform(0.1, 0.4), uniform(0.6, 0.9)]),
        [
            (
                uuid4().hex,
                uniform(0.1, 0.5),
                table_cell_coordinates_factory(),
                [source_bbox_coordinates_factory(), source_bbox_coordinates_factory()],
                entity_id_factory(),
            ),
            (
                uuid4().hex,
                uniform(0.1, 0.5),
                table_cell_coordinates_factory(),
                [source_bbox_coordinates_factory(), source_bbox_coordinates_factory()],
                entity_id_factory(),
            ),
        ],
        source_bbox_coordinates_factory(),
        table_meta,
        [[uniform(0.1, 0.5), uniform(0.1, 0.5)], [uniform(0.1, 0.5), uniform(0.1, 0.5)]],
    )


@pytest.fixture
def extracted_table_factory_with_table_coord(
    ef_factory: ExtractedFieldFactory,
    source_table_coordinates_factory,
    table_meta,
    table_cell_coordinates_factory,
    entity_id_factory,
):
    return lambda: ef_factory.create_table(
        uuid4().hex,
        sorted([uniform(0.1, 0.4), uniform(0.6, 0.9)]),
        sorted([uniform(0.1, 0.4), uniform(0.6, 0.9)]),
        [
            (
                uuid4().hex,
                uniform(0.1, 0.5),
                table_cell_coordinates_factory(),
                [source_table_coordinates_factory(), source_table_coordinates_factory()],
                entity_id_factory(),
            ),
            (
                uuid4().hex,
                uniform(0.1, 0.5),
                table_cell_coordinates_factory(),
                [source_table_coordinates_factory(), source_table_coordinates_factory()],
                entity_id_factory(),
            ),
        ],
        [source_table_coordinates_factory(), source_table_coordinates_factory()],
        table_meta,
        [[uniform(0.1, 0.5), uniform(0.1, 0.5)], [uniform(0.1, 0.5), uniform(0.1, 0.5)]],
    )


@pytest.fixture
def extracted_table_factory_with_text_cell_coord(
    ef_factory: ExtractedFieldFactory,
    source_text_coordinates_factory,
    table_meta,
    source_table_coordinates_factory,
    table_cell_coordinates_factory,
    entity_id_factory,
):
    return lambda: ef_factory.create_table(
        uuid4().hex,
        sorted([uniform(0.1, 0.4), uniform(0.6, 0.9)]),
        sorted([uniform(0.1, 0.4), uniform(0.6, 0.9)]),
        [
            (
                uuid4().hex,
                uniform(0.1, 0.5),
                table_cell_coordinates_factory(),
                [source_text_coordinates_factory(), source_text_coordinates_factory()],
                entity_id_factory(),
            ),
            (
                uuid4().hex,
                uniform(0.1, 0.5),
                table_cell_coordinates_factory(),
                [source_text_coordinates_factory(), source_text_coordinates_factory()],
                entity_id_factory(),
            ),
        ],
        [source_table_coordinates_factory(), source_table_coordinates_factory()],
        table_meta,
        [[uniform(0.1, 0.5), uniform(0.1, 0.5)], [uniform(0.1, 0.5), uniform(0.1, 0.5)]],
    )


@pytest.fixture
def extracted_table_factory_from_dict(
    ef_factory: ExtractedFieldFactory,
    source_table_coordinates_factory,
    table_cell_coordinates,
    build_cells_from_dict,
    build_source_table_coordinates,
):
    def _grid_size(cells: list[dict]) -> tuple[int, int]:
        max_col = 0
        max_row = 0
        for c in cells:
            coord = c["coordinates"]
            max_col = max(max_col, coord["column"] + coord.get("colspan", 1))
            max_row = max(max_row, coord["row"] + coord.get("rowspan", 1))
        return max_col, max_row

    def inner(*args, **kwargs):
        cells = (
            build_cells_from_dict(kwargs["cells"])
            if kwargs.get("cells")
            else [
                (
                    uuid4().hex,
                    uniform(0.1, 0.5),
                    table_cell_coordinates,
                    [source_table_coordinates_factory(), source_table_coordinates_factory()],
                    entity_id_factory(),
                ),
                (
                    uuid4().hex,
                    uniform(0.1, 0.5),
                    table_cell_coordinates,
                    [source_table_coordinates_factory(), source_table_coordinates_factory()],
                    entity_id_factory(),
                ),
            ]
        )

        coordinates = (
            [source_table_coordinates_factory()]
            if not kwargs.get("coordinates")
            else build_source_table_coordinates(kwargs["coordinates"])
        )

        if kwargs.get("columns") is not None:
            columns = kwargs["columns"]
        else:
            needed_cols, _ = _grid_size(kwargs.get("cells", []))
            columns = [float(i) for i in range(max(needed_cols, 2))]

        if kwargs.get("rows") is not None:
            rows = kwargs["rows"]
        else:
            _, needed_rows = _grid_size(kwargs.get("cells", []))
            rows = [float(i) for i in range(max(needed_rows, 2))]

        return ef_factory.create_table(
            field_code=kwargs.get("field_code") or uuid4().hex,
            columns=columns,
            rows=rows,
            cells=cells,
            coordinates=coordinates,
            meta=kwargs.get("meta"),
            paginated_rows=kwargs.get("paginated_rows"),
        )

    return inner


@pytest.fixture
def build_source_table_coordinates():
    def _build_source_table_coordinates(coordinates):
        return [
            SourceTableCoordinates(
                value=el["sourceId"],
                cell_ranges=[
                    CellRange(begin=CellCoordinates(**coord["begin"]))
                    if coord.get("end") is None
                    else CellRange.with_end(
                        begin=CellCoordinates(**coord["begin"]), end=CellCoordinates(**coord["end"])
                    )
                    for coord in el["cellRanges"]
                ],
            )
            for el in coordinates
        ]

    return _build_source_table_coordinates


@pytest.fixture
def build_cells_from_dict():
    def _build_cells_from_dict(cells):
        return [
            (
                cell["value"],
                cell["confidence"],
                TableCellCoordinates(
                    column_span=cell["coordinates"].pop("colspan"),
                    row_span=cell["coordinates"].pop("rowspan"),
                    **cell["coordinates"],
                ),
                [
                    SourceTableCoordinates(
                        value=el["sourceId"],
                        cell_ranges=[
                            CellRange(begin=CellCoordinates(**coord["begin"]))
                            if coord.get("end") is None
                            else CellRange.with_end(
                                begin=CellCoordinates(**coord["begin"]), end=CellCoordinates(**coord["end"])
                            )
                            for coord in el["cellRanges"]
                        ],
                    )
                    for el in cell["sourceTableCoordinates"]
                ],
                EntityId(cell["pk"]) if cell.get("pk") else EntityId(),
            )
            for cell in cells
        ]

    return _build_cells_from_dict


@pytest.fixture
def extracted_string_list_factory(
    ef_factory: ExtractedFieldFactory, extracted_string_factory_with_bbox_coord, aliases_factory
):
    def build_fixture(**kwargs):
        elements = [extracted_string_factory_with_bbox_coord().data, extracted_string_factory_with_bbox_coord().data]
        return ef_factory.create_checkbox_list(
            field_code=uuid4().hex,
            elements=elements,
            aliases=aliases_factory(elements) if kwargs.get("with_aliases") else None,
        )

    return build_fixture


@pytest.fixture
def extracted_checkbox_list_factory(
    ef_factory: ExtractedFieldFactory, extracted_checkbox_factory_with_text_coord, aliases_factory
):
    def build_fixture(**kwargs):
        elements = [
            extracted_checkbox_factory_with_text_coord().data,
            extracted_checkbox_factory_with_text_coord().data,
        ]
        return ef_factory.create_checkbox_list(
            field_code=uuid4().hex,
            elements=elements,
            aliases=aliases_factory(elements) if kwargs.get("with_aliases") else None,
        )

    return build_fixture


@pytest.fixture
def extracted_key_value_pair_list_factory(
    ef_factory: ExtractedFieldFactory,
    extracted_key_value_pair_factory_with_table_coord,
    aliases_factory,
):
    def build_fixture(**kwargs):
        elements = [
            extracted_key_value_pair_factory_with_table_coord().data,
            extracted_key_value_pair_factory_with_table_coord().data,
        ]
        return ef_factory.create_key_value_pair_list(
            field_code=uuid4().hex,
            elements=elements,
            aliases=aliases_factory(elements) if kwargs.get("with_aliases") else None,
        )

    return build_fixture


@pytest.fixture
def extracted_table_list_factory(
    ef_factory: ExtractedFieldFactory, extracted_table_factory_with_bbox_coord, aliases_factory
):
    def build_fixture(**kwargs):
        elements = [extracted_table_factory_with_bbox_coord().data, extracted_table_factory_with_bbox_coord().data]
        return ef_factory.create_table_list(
            field_code=uuid4().hex,
            elements=elements,
            aliases=aliases_factory(elements) if kwargs.get("with_aliases") else None,
        )

    return build_fixture


@pytest.fixture
def document_id_factory():
    return lambda: randint(1, 100)


@pytest.fixture
def aliases_factory():
    def build_fixture(list_of_fields, **kwargs):
        return {field.id: uuid4().hex for field in list_of_fields}

    return build_fixture


@pytest.fixture
def empty_extracted_data(document_id_factory):
    return ExtractedDataFactory.make_extracted_data(document_id_factory())


@pytest.fixture
def extracted_data_factory(
    document_id_factory,
    extracted_table_factory_with_table_coord,
    extracted_table_factory_with_bbox_coord,
    extracted_table_factory_with_text_cell_coord,
    extracted_string_factory_with_bbox_coord,
    extracted_string_factory_with_table_coord,
    extracted_string_factory_with_text_coord,
    extracted_checkbox_factory_with_bbox_coord,
    extracted_checkbox_factory_with_table_coord,
    extracted_checkbox_factory_with_text_coord,
    extracted_key_value_pair_factory_with_bbox_coord,
    extracted_key_value_pair_factory_with_table_coord,
    extracted_key_value_pair_factory_with_text_coord,
    extracted_table_list_factory,
    extracted_checkbox_list_factory,
    extracted_string_list_factory,
    extracted_key_value_pair_list_factory,
):
    def create_edata(*, external_doc_id: int = None, **kwargs):
        extracted_data = ExtractedDataFactory.make_extracted_data(external_doc_id or document_id_factory())
        extracted_data.add_string(extracted_string_factory_with_bbox_coord())
        extracted_data.add_string(extracted_string_factory_with_table_coord())
        extracted_data.add_string(extracted_string_factory_with_text_coord())
        extracted_data.add_checkbox(extracted_checkbox_factory_with_bbox_coord())
        extracted_data.add_checkbox(extracted_checkbox_factory_with_table_coord())
        extracted_data.add_checkbox(extracted_checkbox_factory_with_text_coord())
        extracted_data.add_key_value_pair(extracted_key_value_pair_factory_with_table_coord())
        extracted_data.add_key_value_pair(extracted_key_value_pair_factory_with_bbox_coord())
        extracted_data.add_key_value_pair(extracted_key_value_pair_factory_with_text_coord())
        extracted_data.add_table(extracted_table_factory_with_table_coord())
        extracted_data.add_table(extracted_table_factory_with_bbox_coord())
        extracted_data.add_table(extracted_table_factory_with_text_cell_coord())
        extracted_data.add_table_list(extracted_table_list_factory(with_aliases=True))
        extracted_data.add_table_list(extracted_table_list_factory())
        extracted_data.add_string_list(extracted_string_list_factory())
        extracted_data.add_string_list(extracted_string_list_factory(with_aliases=True))
        extracted_data.add_checkbox_list(extracted_checkbox_list_factory(with_aliases=True))
        extracted_data.add_checkbox_list(extracted_checkbox_list_factory())
        extracted_data.add_key_value_pair_list(extracted_key_value_pair_list_factory(with_aliases=True))
        extracted_data.add_key_value_pair_list(extracted_key_value_pair_list_factory())
        return extracted_data

    return create_edata


@pytest.fixture
def saved_extacted_data_with_with_aliases(
    document_id_factory,
    extracted_string_list_factory,
    extracted_table_list_factory,
    extracted_key_value_pair_list_factory,
    extracted_checkbox_list_factory,
    extracted_data_repository,
):
    edata = ExtractedDataFactory.make_extracted_data(document_id_factory())
    edata.add_string_list(extracted_string_list_factory(with_aliases=True))
    edata.add_table_list(extracted_table_list_factory(with_aliases=True))
    edata.add_key_value_pair_list(extracted_key_value_pair_list_factory(with_aliases=True))
    edata.add_checkbox_list(extracted_checkbox_list_factory(with_aliases=True))

    extracted_data_repository.save(edata)

    return edata
