from typing import Mapping

from deps_extraction.domain.model import FieldDescription

__all__ = ["BasicDescriptionMapper"]


class BasicDescriptionMapper:
    @staticmethod
    def from_dict(_: Mapping[str, int]) -> FieldDescription:  # noqa: WPS605
        return FieldDescription()

    @staticmethod
    def to_dict(_: FieldDescription) -> Mapping[str, int]:  # noqa: WPS605
        return {}
