from typing import Optional

from ...shared import Code, FormatCheck, Guard, ImmutableCheck
from .profile import FieldProfile, FieldType
from .profile.description import FieldDescription

__all__ = ["ExtractionField"]


class ExtractionField:
    code = Guard[Code](Code, ImmutableCheck())
    name = Guard[str](str, ImmutableCheck(), FormatCheck(r"^\S(?:\s?\S)*$"))
    profile = Guard[FieldProfile](FieldProfile, ImmutableCheck())
    required = Guard[bool](bool, ImmutableCheck())
    display_order = Guard[int](int, ImmutableCheck())

    def __init__(
        self,
        code: Code,
        name: str,
        profile: FieldProfile,
        required: bool,
        display_order: int,
    ) -> None:
        self.code = code
        self.name = name
        self.profile = profile
        self.required = required
        self.display_order = display_order

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ExtractionField)  # noqa: WPS222
            and other.code == self.code
            and other.name == self.name
            and other.profile == self.profile
            and other.required == self.required
            and other.display_order == self.display_order
        )

    def __repr__(self) -> str:
        return (
            f"<class '{self.__class__.__name__}': "
            f"{self.code = }, "
            f"{self.name = }, "
            f"{self.profile = }, "
            f"{self.required = }, "
            f"{self.display_order = }>"
        )

    @property
    def type(self) -> FieldType:
        return self.profile.type

    @property
    def description(self) -> FieldDescription:
        return self.profile.description

    def create_updated(
        self,
        name: Optional[str] = None,
        required: Optional[bool] = None,
        description: Optional[FieldDescription] = None,
        display_order: Optional[int] = None,
    ) -> "ExtractionField":
        updated_profile = (
            self.profile.with_updated_description(description) if description is not None else self.profile
        )

        return ExtractionField(
            code=self.code,
            name=name if name is not None else self.name,
            profile=updated_profile,
            required=required if required is not None else self.required,
            display_order=display_order if display_order is not None else self.display_order,
        )
