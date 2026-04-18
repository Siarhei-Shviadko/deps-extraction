from typing import Union

from deps_extraction.domain.model import (
    DateFieldDescription,
    EnumFieldDescription,
    StringFieldDescription,
)

from .date_description import SerializedDateDescription
from .enum_description import SerializedEnumDescription
from .string_description import SerializedStringDescription

__all__ = ["GENERIC_DESCRIPTION_MAP", "DescriptionGenericType"]


DescriptionGenericType = Union[
    SerializedEnumDescription,
    SerializedDateDescription,
    SerializedStringDescription,
]


GENERIC_DESCRIPTION_MAP = {  # noqa: WPS407
    StringFieldDescription: SerializedStringDescription,
    EnumFieldDescription: SerializedEnumDescription,
    DateFieldDescription: SerializedDateDescription,
}
