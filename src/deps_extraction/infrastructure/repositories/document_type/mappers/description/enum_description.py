from typing import Any, Mapping

from deps_extraction.domain.model import EnumFieldDescription

__all__ = ["EnumDescriptionMapper"]


class EnumDescriptionMapper:
    @staticmethod
    def from_dict(raw_description: Mapping[str, Any]) -> EnumFieldDescription:
        return EnumFieldDescription(options=raw_description["options"])

    @staticmethod
    def to_dict(description: EnumFieldDescription) -> Mapping[str, Any]:
        return {"options": description.options}
