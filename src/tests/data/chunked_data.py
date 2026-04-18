import copy
import json

cells_row1 = [
    {
        "value": "a",
        "coordinates": {"column": 0, "row": 0, "colspan": 1, "rowspan": 1},
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [{"sourceId": "string", "cellRanges": [{"begin": {"column": 0, "row": 0}}]}],
        "sourceTextCoordinates": None,
        "pk": "1",
    },
    {
        "value": "b",
        "coordinates": {"column": 1, "row": 0, "colspan": 2, "rowspan": 2},
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [
            {"sourceId": "string", "cellRanges": [{"begin": {"column": 1, "row": 0}, "end": {"column": 2, "row": 1}}]}
        ],
        "sourceTextCoordinates": None,
        "pk": "2",
    },
]

cells_row2 = [
    {
        "value": "d",
        "coordinates": {
            "column": 0,
            "row": 1,
            "colspan": 1,
            "rowspan": 1,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [{"sourceId": "string", "cellRanges": [{"begin": {"column": 0, "row": 1}}]}],
        "sourceTextCoordinates": None,
        "pk": "3",
    }
]
cells_row3 = [
    {
        "value": "g",
        "coordinates": {
            "column": 0,
            "row": 2,
            "colspan": 1,
            "rowspan": 1,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [{"sourceId": "string", "cellRanges": [{"begin": {"column": 0, "row": 2}}]}],
        "sourceTextCoordinates": None,
        "pk": "4",
    },
    {
        "value": "h",
        "coordinates": {
            "column": 1,
            "row": 2,
            "colspan": 1,
            "rowspan": 1,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [{"sourceId": "string", "cellRanges": [{"begin": {"column": 1, "row": 2}}]}],
        "sourceTextCoordinates": None,
        "pk": "5",
    },
    {
        "value": "I",
        "coordinates": {
            "column": 2,
            "row": 2,
            "colspan": 1,
            "rowspan": 2,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [
            {"sourceId": "string", "cellRanges": [{"begin": {"column": 2, "row": 2}, "end": {"column": 2, "row": 3}}]}
        ],
        "sourceTextCoordinates": None,
        "pk": "6",
    },
]
cells_row4 = [
    {
        "value": "K",
        "coordinates": {
            "column": 0,
            "row": 3,
            "colspan": 2,
            "rowspan": 1,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [
            {"sourceId": "string", "cellRanges": [{"begin": {"column": 0, "row": 3}, "end": {"column": 1, "row": 3}}]}
        ],
        "sourceTextCoordinates": None,
        "pk": "7",
    }
]
cells_row5 = [
    {
        "value": "L",
        "coordinates": {
            "column": 0,
            "row": 4,
            "colspan": 1,
            "rowspan": 1,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [{"sourceId": "string", "cellRanges": [{"begin": {"column": 0, "row": 4}}]}],
        "sourceTextCoordinates": None,
        "pk": "8",
    },
    {
        "value": "M",
        "coordinates": {
            "column": 1,
            "row": 4,
            "colspan": 1,
            "rowspan": 2,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [
            {"sourceId": "string", "cellRanges": [{"begin": {"column": 1, "row": 4}, "end": {"column": 1, "row": 5}}]}
        ],
        "sourceTextCoordinates": None,
        "pk": "9",
    },
    {
        "value": "N",
        "coordinates": {
            "column": 2,
            "row": 4,
            "colspan": 1,
            "rowspan": 1,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [{"sourceId": "string", "cellRanges": [{"begin": {"column": 2, "row": 4}}]}],
        "sourceTextCoordinates": None,
        "pk": "10",
    },
]
cells_row6 = [
    {
        "value": "O",
        "coordinates": {
            "column": 0,
            "row": 5,
            "colspan": 1,
            "rowspan": 1,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [{"sourceId": "string", "cellRanges": [{"begin": {"column": 0, "row": 5}}]}],
        "sourceTextCoordinates": None,
        "pk": "11",
    },
    {
        "value": "P",
        "coordinates": {
            "column": 2,
            "row": 5,
            "colspan": 1,
            "rowspan": 1,
        },
        "tableCoordinates": None,
        "confidence": 1.0,
        "sourceBboxCoordinates": None,
        "sourceTableCoordinates": [{"sourceId": "string", "cellRanges": [{"begin": {"column": 2, "row": 5}}]}],
        "sourceTextCoordinates": None,
        "pk": "12",
    },
]

corleone_table_dict_chunk_json = [
    {
        "fieldPk": "76",
        "isInGoldenData": False,
        "data": {
            "coordinates": None,
            "columns": [{"x": 0.0}, {"x": 0.14285714285714285}, {"x": 0.2857142857142857}],
            "rows": [
                {"y": 0.0},
                {"y": 0.09090909090909091},
                {"y": 0.18181818181818182},
                {"y": 0.2727272727272727},
                {"y": 0.3727272727272727},
                {"y": 0.4727272727272727},
            ],
            "tableCoordinates": None,
            "sourceId": None,
            "sourceBboxCoordinates": None,
            "sourceTableCoordinates": [
                {
                    "sourceId": "string",
                    "cellRanges": [{"begin": {"column": 0, "row": 0}, "end": {"column": 2, "row": 5}}],
                }
            ],
            "paginatedRows": None,
            "setIndex": 0,
            "cells": [*cells_row1, *cells_row2, *cells_row3, *cells_row4, *cells_row5, *cells_row6],
        },
    }
]
corleone_table_dict_chunk = json.dumps(corleone_table_dict_chunk_json)
list_chunk_table = {
    "fieldPk": "77",
    "data": [
        copy.deepcopy(corleone_table_dict_chunk_json[0]["data"]),
        copy.deepcopy(corleone_table_dict_chunk_json[0]["data"]),
    ],
}
list_chunk_table_raw = json.dumps(list_chunk_table)

chunk_3_x_2_response = {
    "meta": {"rows_chunk": 2, "chunks_total": 2, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "O",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 2,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "11",
            },
            {
                "value": "P",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 2,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "12",
            },
            {
                "value": "K",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 2,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 0, "row": 3},
                                "end": {"column": 1, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "7",
            },
            {
                "value": "L",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "8",
            },
            {
                "value": "M",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 4},
                                "end": {"column": 1, "row": 5},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "9",
            },
            {
                "value": "N",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "10",
            },
            {
                "value": "I",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 2, "row": 2},
                                "end": {"column": 2, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "6",
            },
        ]
    },
}
chunk_3_x_1_response = {
    "meta": {"rows_chunk": 1, "chunks_total": 2, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "a",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 0}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "1",
            },
            {
                "value": "b",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 0,
                    "colspan": 2,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 0},
                                "end": {"column": 2, "row": 1},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "2",
            },
            {
                "value": "d",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 1}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "3",
            },
            {
                "value": "g",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 2,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "4",
            },
            {
                "value": "h",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 2,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 1, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "5",
            },
            {
                "value": "I",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 2,
                    "colspan": 1,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 2, "row": 2},
                                "end": {"column": 2, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "6",
            },
        ]
    },
}
chunk_4_x_1_response = {
    "meta": {"rows_chunk": 1, "chunks_total": 2, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "a",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 0}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "1",
            },
            {
                "value": "b",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 0,
                    "colspan": 2,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 0},
                                "end": {"column": 2, "row": 1},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "2",
            },
            {
                "value": "d",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 1}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "3",
            },
            {
                "value": "g",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 2,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "4",
            },
            {
                "value": "h",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 2,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 1, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "5",
            },
            {
                "value": "I",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 2,
                    "colspan": 1,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 2, "row": 2},
                                "end": {"column": 2, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "6",
            },
            {
                "value": "K",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 3,
                    "colspan": 2,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 0, "row": 3},
                                "end": {"column": 1, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "7",
            },
        ]
    },
}
chunk_4_x_2_response = {
    "meta": {"rows_chunk": 2, "chunks_total": 2, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "O",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "11",
            },
            {
                "value": "P",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "12",
            },
            {
                "value": "L",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "8",
            },
            {
                "value": "M",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 4},
                                "end": {"column": 1, "row": 5},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "9",
            },
            {
                "value": "N",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "10",
            },
        ]
    },
}
chunk_5_x_1_response = {
    "meta": {"rows_chunk": 1, "chunks_total": 2, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "a",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 0}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "1",
            },
            {
                "value": "b",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 2,
                    "column": 1,
                    "row": 0,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 0},
                                "end": {"column": 2, "row": 1},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "2",
            },
            {
                "value": "d",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 1}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "3",
            },
            {
                "value": "g",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 2,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "4",
            },
            {
                "value": "h",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 1,
                    "row": 2,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 1, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "5",
            },
            {
                "value": "I",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 2,
                    "row": 2,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 2, "row": 2},
                                "end": {"column": 2, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "6",
            },
            {
                "value": "K",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 2,
                    "column": 0,
                    "row": 3,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 0, "row": 3},
                                "end": {"column": 1, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "7",
            },
            {
                "value": "L",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 4,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "8",
            },
            {
                "value": "M",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 1,
                    "row": 4,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 4},
                                "end": {"column": 1, "row": 5},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "9",
            },
            {
                "value": "N",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 2,
                    "row": 4,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "10",
            },
        ]
    },
}
chunk_5_x_2_response = {
    "meta": {"rows_chunk": 2, "chunks_total": 2, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "O",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "11",
            },
            {
                "value": "P",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 2,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "12",
            },
            {
                "value": "M",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 1,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 4},
                                "end": {"column": 1, "row": 5},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "9",
            },
        ]
    },
}
chunk_1_x_1_response = {
    "meta": {"rows_chunk": 1, "chunks_total": 6, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "a",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 0}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "1",
            },
            {
                "value": "b",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 0,
                    "colspan": 2,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 0},
                                "end": {"column": 2, "row": 1},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "2",
            },
        ]
    },
}
chunk_1_x_2_response = {
    "meta": {"rows_chunk": 2, "chunks_total": 6, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "d",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 1}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "3",
            },
            {
                "value": "b",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 2,
                    "column": 1,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 0},
                                "end": {"column": 2, "row": 1},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "2",
            },
        ]
    },
}
chunk_1_x_3_response = {
    "meta": {"rows_chunk": 3, "chunks_total": 6, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "g",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "4",
            },
            {
                "value": "h",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 1,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 1, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "5",
            },
            {
                "value": "I",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 2,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 2, "row": 2},
                                "end": {"column": 2, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "6",
            },
        ]
    },
}
chunk_1_x_4_response = {
    "meta": {"rows_chunk": 4, "chunks_total": 6, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "K",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 2,
                    "column": 0,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 0, "row": 3},
                                "end": {"column": 1, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "7",
            },
            {
                "value": "I",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 2,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 2, "row": 2},
                                "end": {"column": 2, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "6",
            },
        ]
    },
}
chunk_1_x_5_response = {
    "meta": {"rows_chunk": 5, "chunks_total": 6, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "L",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "8",
            },
            {
                "value": "M",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 4},
                                "end": {"column": 1, "row": 5},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "9",
            },
            {
                "value": "N",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "10",
            },
        ]
    },
}
chunk_1_x_6_response = {
    "meta": {"rows_chunk": 6, "chunks_total": 6, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "O",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "11",
            },
            {
                "value": "P",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "12",
            },
            {
                "value": "M",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 4},
                                "end": {"column": 1, "row": 5},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "9",
            },
        ]
    },
}
chunk_2_x_1_response = {
    "meta": {"rows_chunk": 1, "chunks_total": 3, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "a",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 0}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "1",
            },
            {
                "value": "b",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 0,
                    "colspan": 2,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 0},
                                "end": {"column": 2, "row": 1},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "2",
            },
            {
                "value": "d",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 1}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "3",
            },
        ]
    },
}
chunk_2_x_2_response = {
    "meta": {"rows_chunk": 2, "chunks_total": 3, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "g",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "4",
            },
            {
                "value": "h",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 1, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "5",
            },
            {
                "value": "I",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 2, "row": 2},
                                "end": {"column": 2, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "6",
            },
            {
                "value": "K",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 1,
                    "colspan": 2,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 0, "row": 3},
                                "end": {"column": 1, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "7",
            },
        ]
    },
}
chunk_2_x_3_response = {
    "meta": {"rows_chunk": 3, "chunks_total": 3, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "O",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "11",
            },
            {
                "value": "P",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 1,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "12",
            },
            {
                "value": "L",
                "confidence": 1.0,
                "coordinates": {
                    "column": 0,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "8",
            },
            {
                "value": "M",
                "confidence": 1.0,
                "coordinates": {
                    "column": 1,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 4},
                                "end": {"column": 1, "row": 5},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "9",
            },
            {
                "value": "N",
                "confidence": 1.0,
                "coordinates": {
                    "column": 2,
                    "row": 0,
                    "colspan": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "10",
            },
        ]
    },
}
chunk_15_x_1_response = {
    "meta": {"rows_chunk": 1, "chunks_total": 1, "rows_total": 6, "list_index": None},
    "data": {
        "cells": [
            {
                "value": "a",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 0,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 0}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "1",
            },
            {
                "value": "b",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 2,
                    "column": 1,
                    "row": 0,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 0},
                                "end": {"column": 2, "row": 1},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "2",
            },
            {
                "value": "O",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 5,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "11",
            },
            {
                "value": "P",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 2,
                    "row": 5,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 5}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "12",
            },
            {
                "value": "d",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 1,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 1}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "3",
            },
            {
                "value": "g",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 2,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "4",
            },
            {
                "value": "h",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 1,
                    "row": 2,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 1, "row": 2}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "5",
            },
            {
                "value": "I",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 2,
                    "row": 2,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 2, "row": 2},
                                "end": {"column": 2, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "6",
            },
            {
                "value": "K",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 2,
                    "column": 0,
                    "row": 3,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 0, "row": 3},
                                "end": {"column": 1, "row": 3},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "7",
            },
            {
                "value": "L",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 0,
                    "row": 4,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 0, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "8",
            },
            {
                "value": "M",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 1,
                    "row": 4,
                    "rowspan": 2,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [
                            {
                                "begin": {"column": 1, "row": 4},
                                "end": {"column": 1, "row": 5},
                            }
                        ],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "9",
            },
            {
                "value": "N",
                "confidence": 1.0,
                "coordinates": {
                    "colspan": 1,
                    "column": 2,
                    "row": 4,
                    "rowspan": 1,
                },
                "sourceBboxCoordinates": None,
                "sourceTableCoordinates": [
                    {
                        "sourceId": "string",
                        "cellRanges": [{"begin": {"column": 2, "row": 4}, "end": None}],
                    }
                ],
                "sourceTextCoordinates": None,
                "pk": "10",
            },
        ]
    },
}

table_field_chunk_dict = {
    "meta": {"rowsChunk": 1, "listIndex": 0, "chunksTotal": 1, "rowsTotal": 6},
    "cells": [
        *cells_row1,
        *cells_row2,
        *cells_row3,
        *cells_row4,
        *cells_row5,
        *cells_row6,
    ],
}
