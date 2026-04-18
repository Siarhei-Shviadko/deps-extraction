from .guards import Guard, ImmutableCheck, LengthCheck

__all__ = ["TenantId"]


class TenantId:
    id = Guard[str](str, ImmutableCheck(), LengthCheck(max_length=150))

    def __init__(self, id_: str) -> None:
        self.id = id_

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TenantId) and self.id == other.id

    def __repr__(self) -> str:
        return f"<class '{self.__class__.__name__}': {self.id = }>"

    def __call__(self) -> str:
        return self.id
