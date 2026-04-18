from typing import Any

from deps_extracted_data.model import Group


def group_dict(group: Group) -> dict[str, Any]:
    return {"order": group.order, "name": group.name, "elements": group.elements}
