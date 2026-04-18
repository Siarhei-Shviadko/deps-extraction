from typing import Any, Mapping

from deps_extraction.domain.model import DateFieldDescription

__all__ = ["DateDescriptionMapper"]


class DateDescriptionMapper:
    @staticmethod
    def from_dict(raw_description: Mapping[str, Any]) -> DateFieldDescription:
        return DateFieldDescription(
            format=raw_description["format"],
            display_char_limit=raw_description.get("display_char_limit"),
        )

    @staticmethod
    def to_dict(description: DateFieldDescription) -> Mapping[str, Any]:
        return {
            "format": description.format,
            "display_char_limit": description.display_char_limit,
        }
