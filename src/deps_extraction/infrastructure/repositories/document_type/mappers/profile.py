from typing import Any, Mapping

from deps_extraction.domain.model import FieldDescription, FieldProfile, FieldType

from .description import (
    BASE_TYPES_MAPPING,
    BasicDescriptionMapper,
    DictDescriptionMapper,
    ListDescriptionMapper,
    TableDescriptionMapper,
)

__all__ = ["ProfileMapper"]


PROFILE_DESCRIPTION_MAP = {  # noqa: WPS407
    **BASE_TYPES_MAPPING,
    FieldType.DICT: DictDescriptionMapper,
    FieldType.TABLE: TableDescriptionMapper,
    FieldType.LIST: ListDescriptionMapper,
}


class ProfileMapper:
    @staticmethod
    def to_dict(profile: FieldProfile) -> Mapping[str, Any]:
        if type(profile.description) == FieldDescription:  # noqa: WPS516
            raw_description = BasicDescriptionMapper.to_dict(profile.description)
        else:
            raw_description = PROFILE_DESCRIPTION_MAP[profile.type].to_dict(profile.description)

        return {
            "description": raw_description,
            "type": profile.type.value,
        }

    @staticmethod
    def from_dict(raw_profile: Mapping[str, Any]) -> FieldProfile:
        field_type = FieldType(raw_profile["type"])

        if (
            list(raw_profile["description"].keys()) == ["display_order"] or not raw_profile["description"]
        ):  # noqa: WPS504
            description = BasicDescriptionMapper.from_dict(raw_profile["description"])
        else:
            description = PROFILE_DESCRIPTION_MAP[field_type].from_dict(raw_profile["description"])

        return FieldProfile(
            type_=field_type,
            description=description,
        )
