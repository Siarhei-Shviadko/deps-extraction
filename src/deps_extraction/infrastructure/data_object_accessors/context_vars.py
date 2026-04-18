import contextvars

from deps_extraction.infrastructure.repositories.extracted_data.types import (
    CommonDictType,
)

user: contextvars.ContextVar[CommonDictType] = contextvars.ContextVar("user")
