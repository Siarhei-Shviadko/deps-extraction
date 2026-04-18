from .base import BusinessException, NotFoundError

__all__ = [
    "DocumentTypeNotFound",
    "FieldNotFound",
    "InconsistentProfileDescription",
    "FieldAlreadyExistsError",
    "InvariantViolation",
    "AttachmentExtractorConflict",
    "ExtractorNotFound",
]


class DocumentTypeNotFound(NotFoundError):
    code = "document_type_not_found"

    def __init__(self, doc_type_id: str) -> None:
        super().__init__(f"Document type with id: `{doc_type_id}` not found")


class FieldNotFound(NotFoundError):
    code = "field_not_found"

    def __init__(self, doc_type_id: str, field_code: str) -> None:
        super().__init__(f"Document type `{doc_type_id}` doesn't contain field with code: `{field_code}`")


class FieldAlreadyExistsError(BusinessException):
    def __init__(self, code: str) -> None:
        self.code = f"Field with code '{code}' already exists in the extractor."


class InvariantViolation(BusinessException):
    code = "invariant_violation"


class InconsistentProfileDescription(BusinessException):
    code = "profile_not_consistent"

    def __init__(self, type_: str, desc_class_name: str) -> None:
        super().__init__(f"Profile has `{type_}` type that not consistent with description class: `{desc_class_name}`")


class AttachmentExtractorConflict(BusinessException):
    code = "attachment_conflict"

    def __init__(self, document_type: str, new_extractor: str, previous_extractor: str) -> None:
        super().__init__(
            f"Cannot attach {new_extractor} extractor."
            f"Extractor {previous_extractor} is already attached for document type {document_type}!",
        )


class ExtractorNotFound(NotFoundError):
    code = "extractor_not_found"

    def __init__(self, document_type: str) -> None:
        super().__init__(f"Cannot find appropriate extractor for document type: {document_type}")
