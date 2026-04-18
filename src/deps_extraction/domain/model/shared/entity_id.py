import uuid
from typing import Optional

from .guards import Guard, ImmutableCheck, LengthCheck

__all__ = ["EntityId"]


class EntityId:
    value = Guard[str](str, ImmutableCheck(), LengthCheck(max_length=150))

    def __init__(self, value: Optional[str] = None) -> None:
        self.value = value or uuid.uuid4().hex

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EntityId) and self.value == other.value

    def __call__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __str__(self) -> str:
        return self.value
