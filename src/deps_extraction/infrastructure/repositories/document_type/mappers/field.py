from typing import Any, Mapping

from deps_extraction.domain.model import Code, ExtractionField

from .profile import ProfileMapper

__all__ = ["FieldMapper"]


class FieldMapper:
    @staticmethod
    def to_dict(field: ExtractionField) -> Mapping[str, Any]:
        return {
            "code": field.code(),
            "name": field.name,
            "profile": ProfileMapper.to_dict(field.profile),
            "required": field.required,
            "display_order": field.display_order,
        }

    @staticmethod
    def from_dict(raw_field: Mapping[str, Any]) -> ExtractionField:
        return ExtractionField(
            code=Code(raw_field["code"]),
            name=raw_field["name"],
            profile=ProfileMapper.from_dict(raw_field["profile"]),
            required=raw_field["required"],
            display_order=raw_field.get("display_order", 0),
        )
