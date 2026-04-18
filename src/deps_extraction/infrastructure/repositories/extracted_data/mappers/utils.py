from typing import Any

__all__ = ["build_dict_for_meta_column_from"]


def build_dict_for_meta_column_from(keys: tuple[str, ...], values: tuple[Any, ...]) -> dict[str, Any]:
    result = {}
    for key, value in zip(keys, values):
        if value is not None:
            result[key] = value

    return result
