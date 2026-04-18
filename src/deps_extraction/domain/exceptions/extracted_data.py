from .base import ExtractionException, NotFoundError

__all__ = [
    "ExtractedDataNotFound",
    "ExtractedFieldNotFound",
    "UnknownFieldType",
    "UnknownExtractedDataValueType",
    "ExtractedDataForbidden",
    "ChunkedExtractedDataError",
    "ExtractedFieldUpdateAliasesError",
]


class ExtractedDataNotFound(NotFoundError):
    code = "extracted_data_not_found"

    def __init__(self, pk: int):
        super().__init__(f"Extracted data with pk: `{pk}` not found")


class ExtractedFieldNotFound(NotFoundError):
    code = "extracted_field_not_found"

    def __init__(self, field_codes: list[str]):
        super().__init__(f"Extracted fields not found for field codes: {field_codes}")


class UnknownFieldType(ExtractionException):
    code = "unknown_field_type"


class UnknownExtractedDataValueType(ExtractionException):
    code = "unknown_extracted_data_value_type"


class ExtractedDataForbidden(ExtractionException):
    code = "extracted_data_forbidden"


class ChunkedExtractedDataError(ExtractionException):
    code = "chunked_extracted_data_error"


class ExtractedFieldUpdateAliasesError(ExtractionException):
    code = "extracted_field_update_aliases_error"
