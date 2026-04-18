from typing import Union

from .char_type import *
from .date_description import *
from .description import *
from .dict_description import *
from .enum_description import *
from .list_description import *
from .string_description import *
from .table_description import *

__all__ = (
    description.__all__
    + string_description.__all__
    + enum_description.__all__
    + date_description.__all__
    + dict_description.__all__
    + table_description.__all__
    + list_description.__all__
    + char_type.__all__
)

Description = Union[
    date_description.DateFieldDescription,
    description.FieldDescription,
    dict_description.DictFieldDescription,
    enum_description.EnumFieldDescription,
    list_description.ListFieldDescription,
    string_description.StringFieldDescription,
    table_description.TableFieldDescription,
]
