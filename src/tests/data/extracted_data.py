import random
import uuid

from tests.data.table_data import (
    table_cell_coordinates_dict,
    table_meta,
    table_paginated_rows,
)
from tests.factories import (
    TableCellCoordinatesFactory,
    TableMetaFactory,
    TableRowFactory,
)

FIELD_ID = uuid.uuid4().hex

full_extracted_data_without_optional_elements = [
    {
        "id": uuid.uuid4().hex,
        "field_code": "bac1cac679e04511aabd20eea810216e",
        "field_type": "string",
        "meta": {"value_type": "string"},
        "index": "",
        "value": "dc6a9260e40e48eab6362d1a770be472",
        "table_cell_coordinates": None,
        "confidence": 0.6317719538283806,
        "source_bbox_coordinates": [
            {
                "source_id": "b0ea73288737421ebb19731e56455bc9",
                "bboxes": [
                    {
                        "x": 0.39493674486405655,
                        "y": 0.08245817717250627,
                        "h": 0.03052935254724212,
                        "w": 0.17414546622383428,
                    },
                ],
            },
        ],
        "source_table_coordinates": [
            {
                "source_id": "b0ea73288737421ebb19731e56455bc9",
                "cell_ranges": [
                    {"begin": {"row": 10, "column": 23}},
                ],
            },
            {
                "source_id": "b0ea73288737421ebb19731e56455bc9",
                "cell_ranges": [],
            },
        ],
        "source_text_coordinates": [
            {
                "source_id": "b0ea73288737421ebb19731e56455bc9",
                "char_ranges": [{"begin": 23, "end": 10}],
            },
            {
                "source_id": "b0ea73288737421ebb19731e56455bc9",
                "char_ranges": [],
            },
        ],
        "document_id": 89,
        "groups": [],
    },
    {
        "id": uuid.uuid4().hex,
        "field_code": "099456b91f904e6c86352eb17d4f4c75",
        "field_type": "key_value_pair",
        "meta": None,
        "index": "kv_pair",
        "value": None,
        "confidence": None,
        "table_cell_coordinates": None,
        "source_bbox_coordinates": None,
        "source_table_coordinates": None,
        "source_text_coordinates": None,
        "document_id": 89,
        "groups": [],
    },
    {
        "id": uuid.uuid4().hex,
        "field_code": "099456b91f904e6c86352eb17d4f4c75",
        "field_type": "key_value_pair",
        "meta": {"value_type": "string"},
        "index": "key",
        "value": "2cdaa8b7f3da4190a54dcabad4afb7d8",
        "confidence": 0.5061123204751953,
        "table_cell_coordinates": None,
        "source_bbox_coordinates": [],
        "source_table_coordinates": [],
        "source_text_coordinates": [],
        "document_id": 89,
        "groups": [],
    },
    {
        "id": uuid.uuid4().hex,
        "field_code": "099456b91f904e6c86352eb17d4f4c75",
        "field_type": "key_value_pair",
        "meta": {"value_type": "string"},
        "index": "value",
        "value": "2cdaa8b7f3da4190a54dcabad4afb7d8",
        "confidence": 0.24365809449339457,
        "table_cell_coordinates": None,
        "source_bbox_coordinates": [],
        "source_table_coordinates": [],
        "source_text_coordinates": [],
        "document_id": 89,
        "groups": [],
    },
    {
        "id": uuid.uuid4().hex,
        "field_code": "5dbfd0e89f884b589dc2e05018d2c151",
        "field_type": "table",
        "value": None,
        "confidence": None,
        "index": "table",
        "meta": {
            "columns": [0.10, 0.55],
            "rows": [0.10, 0.45],
        },
        "table_cell_coordinates": None,
        "source_bbox_coordinates": None,
        "source_table_coordinates": [],
        "source_text_coordinates": None,
        "document_id": 89,
        "groups": [],
    },
    {
        "id": uuid.uuid4().hex,
        "field_code": "81f9143c6895488ab611898390d4050a",
        "field_type": "table_list",
        "value": "9a7f54866a12494fac6e1bf4bdbfdfbf",
        "confidence": 0.14238830805980213,
        "index": "0.cell.0",
        "table_cell_coordinates": {"column": 0, "row": 0, "column_span": 1, "row_span": 1},
        "meta": None,
        "source_bbox_coordinates": None,
        "source_table_coordinates": None,
        "source_text_coordinates": None,
        "document_id": 89,
        "groups": [],
    },
    {
        "id": uuid.uuid4().hex,
        "confidence": None,
        "value": None,
        "field_code": "81f9143c6895488ab611898390d4050a",
        "field_type": "table_list",
        "index": "0.table",
        "meta": {
            "columns": [0.30, 0.70],
            "rows": [0.20, 0.60],
        },
        "table_cell_coordinates": None,
        "source_bbox_coordinates": None,
        "source_table_coordinates": None,
        "source_text_coordinates": None,
        "document_id": 89,
        "groups": [],
    },
]
string_data_dict_without_coordinates = {
    "id": uuid.uuid4().hex,
    "value": uuid.uuid4().hex,
    "confidence": random.random(),
    "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
    "sourceTableCoordinates": None,
    "sourceTextCoordinates": None,
    "setIndex": 1,
}
string_data_dict_bbox_coordinates = {
    "id": uuid.uuid4().hex,
    "value": uuid.uuid4().hex,
    "confidence": random.choice([None, random.random()]),
    "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
    "setIndex": 2,
}
string_data_dict_table_coordinates = {
    "id": uuid.uuid4().hex,
    "value": uuid.uuid4().hex,
    "confidence": random.choice([None, random.random()]),
    "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
    "setIndex": 2,
}
string_data_dict_text_coordinates = {
    "id": uuid.uuid4().hex,
    "value": uuid.uuid4().hex,
    "confidence": random.choice([None, random.random()]),
    "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
    "setIndex": 3,
}
list_string_data_dict = [
    string_data_dict_bbox_coordinates,
    string_data_dict_table_coordinates,
    string_data_dict_text_coordinates,
]
empty_list: list = []
kv_data_dict_only_key = {
    "id": uuid.uuid4().hex,
    "key": {
        "id": uuid.uuid4().hex,
        "value": uuid.uuid4().hex,
        "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
        "confidence": random.random(),
        "setIndex": 1,
    },
    "value": {
        "id": uuid.uuid4().hex,
        "value": "",
        "sourceBboxCoordinates": None,
        "confidence": None,
    },
}
kv_data_dict_only_value = {
    "id": uuid.uuid4().hex,
    "key": {
        "id": uuid.uuid4().hex,
        "value": "",
        "sourceBboxCoordinates": None,
        "confidence": None,
    },
    "value": {
        "id": uuid.uuid4().hex,
        "value": uuid.uuid4().hex,
        "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
        "confidence": random.random(),
        "setIndex": 1,
    },
}

kv_data_dict_bbox_coordinates = {
    "id": uuid.uuid4().hex,
    "key": {
        "id": uuid.uuid4().hex,
        "value": uuid.uuid4().hex,
        "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
        "confidence": random.choice([None, random.random()]),
        "setIndex": 1,
    },
    "value": {
        "id": uuid.uuid4().hex,
        "value": uuid.uuid4().hex,
        "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
        "confidence": random.choice([None, random.random()]),
        "setIndex": 1,
    },
}
kv_data_dict_table_coordinates = {
    "id": uuid.uuid4().hex,
    "key": {
        "id": uuid.uuid4().hex,
        "value": uuid.uuid4().hex,
        "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
        "confidence": random.choice([None, random.random()]),
        "setIndex": 2,
    },
    "value": {
        "id": uuid.uuid4().hex,
        "value": uuid.uuid4().hex,
        "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
        "confidence": random.choice([None, random.random()]),
        "setIndex": 2,
    },
}
kv_data_dict_text_coordinates = {
    "id": uuid.uuid4().hex,
    "key": {
        "id": uuid.uuid4().hex,
        "value": uuid.uuid4().hex,
        "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
        "confidence": random.choice([None, random.random()]),
        "setIndex": 3,
    },
    "value": {
        "id": uuid.uuid4().hex,
        "value": uuid.uuid4().hex,
        "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
        "confidence": random.choice([None, random.random()]),
        "setIndex": 3,
    },
}
list_kv_data_dict = [
    kv_data_dict_bbox_coordinates,
    kv_data_dict_table_coordinates,
    kv_data_dict_text_coordinates,
]
table_data_dict_without_coordinates = {
    "id": uuid.uuid4().hex,
    "columns": [{"x": random.random()}],
    "rows": [{"y": random.random()}],
    "sourceBboxCoordinates": None,
    "meta": random.choice([None, table_meta(TableMetaFactory())]),
    "paginatedRows": random.choice(
        [None, table_paginated_rows([[TableRowFactory() for _ in range(2)] for _ in range(2)])]
    ),
    "cells": [
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": table_cell_coordinates_dict(TableCellCoordinatesFactory()),
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": table_cell_coordinates_dict(TableCellCoordinatesFactory()),
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": table_cell_coordinates_dict(TableCellCoordinatesFactory()),
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
    ],
}
table_data_dict_bbox_coordinates = {
    "id": uuid.uuid4().hex,
    "columns": [{"x": 0.15}, {"x": 0.85}],
    "rows": [{"y": 0.20}, {"y": 0.80}],
    "sourceBboxCoordinates": {"sourceId": uuid.uuid4().hex, "bboxes": []},
    "paginatedRows": None,
    "cells": [
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 0, "column_span": 1, "row_span": 1},
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 1, "row": 0, "column_span": 1, "row_span": 1},
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 1, "column_span": 1, "row_span": 1},
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
    ],
    "set_index": 1,
}
table_data_dict_table_coordinates = {
    "id": uuid.uuid4().hex,
    "columns": [{"x": 0.12}, {"x": 0.92}],
    "rows": [{"y": 0.18}, {"y": 0.88}],
    "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
    "meta": None,
    "paginatedRows": None,
    "cells": [
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 0, "column_span": 1, "row_span": 1},
            "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 1, "row": 0, "column_span": 1, "row_span": 1},
            "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 1, "column_span": 1, "row_span": 1},
            "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
            "pk": uuid.uuid4().hex,
        },
    ],
    "setIndex": 1,
}
table_data_dict_text_coordinates_for_cells = {
    "id": uuid.uuid4().hex,
    "columns": [{"x": 0.10}, {"x": 0.90}],
    "rows": [{"y": 0.14}, {"y": 0.86}],
    "sourceBboxCoordinates": {"sourceId": uuid.uuid4().hex, "bboxes": []},
    "meta": None,
    "paginatedRows": None,
    "cells": [
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 0, "column_span": 1, "row_span": 1},
            "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 1, "row": 0, "column_span": 1, "row_span": 1},
            "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 1, "column_span": 1, "row_span": 1},
            "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
            "pk": uuid.uuid4().hex,
        },
    ],
    "setIndex": 2,
}

table_chunked_data_dict_bbox_coordinates = {
    "cells": [
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 0, "column_span": 1, "row_span": 1},
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 1, "row": 0, "column_span": 1, "row_span": 1},
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 1, "column_span": 1, "row_span": 1},
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
    ],
    "startPosition": random.randint(1, 10),
    "listIndex": random.choice([random.randint(1, 10), None]),
}
table_chunked_data_dict_table_coordinates = {
    "cells": [
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 0, "column_span": 1, "row_span": 1},
            "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 1, "row": 0, "column_span": 1, "row_span": 1},
            "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 1, "column_span": 1, "row_span": 1},
            "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
            "pk": uuid.uuid4().hex,
        },
    ],
    "startPosition": random.randint(1, 10),
    "listIndex": random.choice([random.randint(1, 10), None]),
}
table_chunked_data_dict_text_coordinates = {
    "cells": [
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 0, "column_span": 1, "row_span": 1},
            "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 1, "row": 0, "column_span": 1, "row_span": 1},
            "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
            "pk": uuid.uuid4().hex,
        },
        {
            "value": uuid.uuid4().hex,
            "confidence": random.choice([None, random.random()]),
            "coordinates": {"column": 0, "row": 1, "column_span": 1, "row_span": 1},
            "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
            "pk": uuid.uuid4().hex,
        },
    ],
    "startPosition": random.randint(0, 10),
    "listIndex": random.choice([random.randint(1, 10), None]),
}

table_info_dict_bbox_coordinates = {
    "info": {
        "id": FIELD_ID,
        "columns": [{"x": 0.10}, {"x": 0.90}],
        "rows": [{"y": 0.14}, {"y": 0.86}],
        "sourceBboxCoordinates": {"sourceId": uuid.uuid4().hex, "bboxes": []},
    },
    "listIndex": None,
}
table_info_dict_bbox_coordinates_list_of_tables_without_aliases = {
    "info": {
        "id": FIELD_ID,
        "columns": [{"x": 0.11}, {"x": 0.89}],
        "rows": [{"y": 0.14}, {"y": 0.86}],
        "sourceBboxCoordinates": {"sourceId": uuid.uuid4().hex, "bboxes": []},
    },
    "listIndex": 2,
}
table_info_dict_bbox_coordinates_list_of_tables_with_aliases = {
    "info": {
        "id": FIELD_ID,
        "columns": [{"x": 0.12}, {"x": 0.88}],
        "rows": [{"y": 0.14}, {"y": 0.86}],
        "sourceBboxCoordinates": {"sourceId": uuid.uuid4().hex, "bboxes": []},
        "alias": "Table alias",
    },
    "listIndex": 1,
}
table_info_dict_table_coordinates = {
    "info": {
        "id": FIELD_ID,
        "columns": [{"x": 0.13}, {"x": 0.87}],
        "rows": [{"y": 0.14}, {"y": 0.86}],
        "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
    },
    "listIndex": None,
}

list_table_data_dict = [
    table_data_dict_bbox_coordinates,
    table_data_dict_table_coordinates,
    table_data_dict_text_coordinates_for_cells,
]

checkmark_data_dict_bbox_coordinates = {
    "id": uuid.uuid4().hex,
    "value": random.choice([True, False]),
    "confidence": random.choice([None, random.random()]),
    "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
    "setIndex": 1,
}
checkmark_data_dict_table_coordinates = {
    "id": uuid.uuid4().hex,
    "value": random.choice([True, False]),
    "confidence": random.choice([None, random.random()]),
    "sourceTableCoordinates": [{"sourceId": uuid.uuid4().hex, "cellRanges": []}],
    "setIndex": 1,
}
checkmark_data_dict_text_coordinates = {
    "id": uuid.uuid4().hex,
    "value": random.choice([True, False]),
    "confidence": random.choice([None, random.random()]),
    "sourceTextCoordinates": [{"sourceId": uuid.uuid4().hex, "charRanges": []}],
    "setIndex": 2,
}
list_checkmark_data_dict = [
    checkmark_data_dict_bbox_coordinates,
    checkmark_data_dict_table_coordinates,
    checkmark_data_dict_text_coordinates,
]

string_data_dict_without_id = {
    "value": uuid.uuid4().hex,
    "confidence": random.random(),
    "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
}
list_string_data_dict_without_id = [string_data_dict_without_id]
kv_data_dict_without_id = {
    "key": {
        "value": uuid.uuid4().hex,
        "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
        "confidence": random.random(),
    },
    "value": {
        "value": uuid.uuid4().hex,
        "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
        "confidence": None,
    },
}
list_kv_data_dict_without_id = [kv_data_dict_without_id]
table_data_dict_without_id = {
    "columns": [{"x": 0.15}, {"x": 0.85}],
    "rows": [{"y": 0.20}, {"y": 0.80}],
    "sourceBboxCoordinates": {"sourceId": uuid.uuid4().hex, "bboxes": []},
    "meta": None,
    "paginatedRows": None,
    "cells": [
        {
            "value": uuid.uuid4().hex,
            "confidence": None,
            "coordinates": {"column": 0, "row": 0, "column_span": 1, "row_span": 1},
            "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
            "pk": uuid.uuid4().hex,
        },
    ],
}
list_table_data_dict_without_id = [table_data_dict_without_id]
checkmark_data_dict_without_id = {
    "value": random.choice([True, False]),
    "confidence": random.choice([None, random.random()]),
    "sourceBboxCoordinates": [{"sourceId": uuid.uuid4().hex, "bboxes": []}],
}
list_checkmark_data_dict_without_id = [checkmark_data_dict_without_id]
