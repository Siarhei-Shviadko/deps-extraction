from typing import Any, Mapping

from deps_extraction.domain.model import CharType, StringFieldDescription

__all__ = ["StringDescriptionMapper"]


class StringDescriptionMapper:
    @staticmethod
    def from_dict(raw_description: Mapping[str, Any]) -> StringFieldDescription:
        return StringFieldDescription(
            char_type=CharType(raw_description["char_type"]) if raw_description.get("char_type") else None,
            char_whitelist=raw_description.get("char_whitelist"),
            char_blacklist=raw_description.get("char_blacklist"),
            display_char_limit=raw_description.get("display_char_limit"),
        )

    @staticmethod
    def to_dict(description: StringFieldDescription) -> Mapping[str, Any]:
        return {
            "char_type": description.char_type.value if description.char_type else None,
            "char_whitelist": description.char_whitelist,
            "char_blacklist": description.char_blacklist,
            "display_char_limit": description.display_char_limit,
        }
