from typing import Any

from deps_extracted_data.model.extracted_data import ExtractedData, Group

__all__ = ["GroupMapper"]


class GroupMapper:
    @staticmethod
    def to_dict(edata: ExtractedData) -> dict[str, Any]:
        return {
            "document_id": edata.document_id,
            "groups": [GroupMapper.build_dict_from_group(group) for group in edata.groups],
        }

    @staticmethod
    def from_dict(raw_group: dict[str, Any]) -> Group:
        group = Group(order=raw_group["order"], name=raw_group["name"])
        group.merge_elements(raw_group["elements"])
        return group

    @staticmethod
    def build_dict_from_group(group: Group) -> dict[str, Any]:
        return {"order": group.order, "name": group.name, "elements": group.elements}
