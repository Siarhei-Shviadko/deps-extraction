from typing import Union

from .date_description import *
from .dict_description import *
from .enum_description import *
from .list_description import *
from .string_description import *
from .table_description import *
from .type_mapping import *

__all__ = (
    date_description.__all__
    + enum_description.__all__
    + dict_description.__all__
    + list_description.__all__
    + string_description.__all__
    + table_description.__all__
    + type_mapping.__all__
)

SerializedDescription = Union[
    SerializedTableDescription,
    SerializedListDescription,
    SerializedDictDescription,
    SerializedDateDescription,
    SerializedEnumDescription,
    SerializedStringDescription,
]


DESCRIPTION_MAP = {  # noqa: WPS407
    **GENERIC_DESCRIPTION_MAP,
    dict_description.DictFieldDescription: SerializedDictDescription,
    table_description.TableFieldDescription: SerializedTableDescription,
    list_description.ListFieldDescription: SerializedListDescription,
}
