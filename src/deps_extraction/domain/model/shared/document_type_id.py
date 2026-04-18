from typing import Optional
from uuid import uuid4

from .guards import Guard, ImmutableCheck, LengthCheck

__all__ = ["DocumentTypeId"]


class DocumentTypeId:
    id = Guard[str](str, ImmutableCheck(), LengthCheck())

    def __init__(self, id_: Optional[str] = None) -> None:
        self.id = id_ or uuid4().hex

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DocumentTypeId) and other.id == self.id

    def __call__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}': {self.id = }>"
