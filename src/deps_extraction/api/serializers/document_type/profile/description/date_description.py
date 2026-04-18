from typing import Optional

from pydantic import Field

from deps_extraction.domain.model import DateFieldDescription

from ....configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["SerializedDateDescription"]


class SerializedDateDescription(ConfiguredBaseSerializer):
    format: str
    display_char_limit: Optional[int] = Field(None, alias="displayCharLimit")

    @classmethod
    def from_model(cls, description: DateFieldDescription) -> "SerializedDateDescription":
        return cls(
            format=description.format,
            display_char_limit=description.display_char_limit,
        )

    def to_model(self) -> DateFieldDescription:
        return DateFieldDescription(
            format=self.format,
            display_char_limit=self.display_char_limit,
        )
