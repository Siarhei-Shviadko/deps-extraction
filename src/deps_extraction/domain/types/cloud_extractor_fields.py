from typing import TypedDict, Union

__all__ = ["RawDescription", "RawTableDescription"]


class RawDateDescription(TypedDict):
    format: str


class RawColumnDescription(TypedDict):
    title: str
    type: str


class RawTableDescription(TypedDict):
    columns: list[RawColumnDescription]


RawDescription = Union[RawTableDescription, RawDateDescription]
