from typing import Any, TypedDict

__all__ = ["ExtractionFieldData"]


class ExtractionFieldData(TypedDict):
    document_type_id: str
    code: str
    name: str

    type: str

    required: bool
    order: int | None
    confidential: bool
    read_only: bool

    description: dict[str, Any] | None
