from deps_extraction.domain.model import FieldType

from .date_description import DateDescriptionMapper
from .enum_description import EnumDescriptionMapper
from .string_description import StringDescriptionMapper

__all__ = ["BASE_TYPES_MAPPING"]


BASE_TYPES_MAPPING = {  # noqa: WPS407
    FieldType.STRING: StringDescriptionMapper,
    FieldType.ENUM: EnumDescriptionMapper,
    FieldType.DATE: DateDescriptionMapper,
    FieldType.CHECKMARK: StringDescriptionMapper,
}
