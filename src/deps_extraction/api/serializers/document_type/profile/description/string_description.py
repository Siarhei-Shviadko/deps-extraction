from typing import Optional

from pydantic import Field

from deps_extraction.domain.model import CharType, StringFieldDescription

from ....configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["SerializedStringDescription"]


class SerializedStringDescription(ConfiguredBaseSerializer):
    char_type: Optional[CharType] = Field(None, alias="charType")
    char_whitelist: Optional[str] = Field(None, alias="charWhitelist")
    char_blacklist: Optional[str] = Field(None, alias="charBlacklist")
    display_char_limit: Optional[int] = Field(None, alias="displayCharLimit")

    def to_model(self) -> StringFieldDescription:
        return StringFieldDescription(
            char_type=self.char_type,
            char_whitelist=self.char_whitelist,
            char_blacklist=self.char_blacklist,
            display_char_limit=self.display_char_limit,
        )

    @classmethod
    def from_model(cls, description: StringFieldDescription) -> "SerializedStringDescription":
        return cls(
            char_type=description.char_type,
            char_whitelist=description.char_whitelist,
            char_blacklist=description.char_blacklist,
            display_char_limit=description.display_char_limit,
        )
