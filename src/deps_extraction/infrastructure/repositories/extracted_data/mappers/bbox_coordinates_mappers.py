from functools import singledispatch
from typing import Optional, Union, overload

from deps_extracted_data import Bbox, SourceBboxCoordinates

from deps_extraction.infrastructure.repositories.extracted_data.types import (
    CommonDictType,
    ListOfDictsType,
)

__all__ = [
    "build_dict_from_source_bbox_coordinates",
    "build_source_bbox_coordinates_from_dict",
    "BboxMapper",
]


class BboxMapper:
    @staticmethod
    def to_dict(bbox: Bbox) -> CommonDictType:
        return {"x": bbox.x, "y": bbox.y, "h": bbox.h, "w": bbox.w}

    @staticmethod
    def from_dict(bbox_dict: CommonDictType) -> Bbox:
        x, y = bbox_dict["x"], bbox_dict["y"]
        w, h = bbox_dict["w"], bbox_dict["h"]
        return Bbox(x=x, y=y, w=w, h=h)


def _build_dict_from_source_bbox_coordinates(source_bbox: SourceBboxCoordinates) -> CommonDictType:
    bboxes = [BboxMapper.to_dict(bbox) for bbox in source_bbox.bboxes]
    return {"source_id": source_bbox.source_id.value, "bboxes": bboxes}


@singledispatch
def _overloaded_build_dict_from_source_bbox_coordinates(
    source_bbox_coordinates: Optional[Union[SourceBboxCoordinates, list[SourceBboxCoordinates]]],
) -> Optional[Union[CommonDictType, ListOfDictsType]]:
    raise TypeError(type(source_bbox_coordinates))


@_overloaded_build_dict_from_source_bbox_coordinates.register
def _from_none(source_bbox_coordinates: None) -> None:
    return source_bbox_coordinates


@_overloaded_build_dict_from_source_bbox_coordinates.register
def _from_source_bbox(source_bbox_coordinates: SourceBboxCoordinates) -> CommonDictType:
    return _build_dict_from_source_bbox_coordinates(source_bbox_coordinates)


@_overloaded_build_dict_from_source_bbox_coordinates.register(list)
def _from_source_bbox_list(source_bbox_coordinates: list[SourceBboxCoordinates]) -> ListOfDictsType:
    return [_build_dict_from_source_bbox_coordinates(source_bbox) for source_bbox in source_bbox_coordinates]


@overload
def build_dict_from_source_bbox_coordinates(source_bbox_coordinates: None) -> None:  # type: ignore
    pass


@overload
def build_dict_from_source_bbox_coordinates(source_bbox_coordinates: SourceBboxCoordinates) -> CommonDictType:
    pass


@overload
def build_dict_from_source_bbox_coordinates(  # type: ignore
    source_bbox_coordinates: list[SourceBboxCoordinates],
) -> ListOfDictsType:
    pass


def build_dict_from_source_bbox_coordinates(
    source_bbox_coordinates: Optional[Union[SourceBboxCoordinates, list[SourceBboxCoordinates]]],
) -> Optional[Union[CommonDictType, ListOfDictsType]]:
    return _overloaded_build_dict_from_source_bbox_coordinates(source_bbox_coordinates)


def _build_source_bbox_coordinates_from_dict(source_bbox_coordinates_dict: CommonDictType) -> SourceBboxCoordinates:
    return SourceBboxCoordinates(
        value=source_bbox_coordinates_dict["source_id"],
        bboxes=[BboxMapper.from_dict(bbox_dict) for bbox_dict in source_bbox_coordinates_dict["bboxes"]],
    )


@singledispatch
def _overloaded_build_source_bbox_coordinates_from_dict(source_bbox_dict):
    raise TypeError(type(source_bbox_dict))


@_overloaded_build_source_bbox_coordinates_from_dict.register
def _to_none(source_bbox_dict: None) -> None:
    return source_bbox_dict


@_overloaded_build_source_bbox_coordinates_from_dict.register(dict)
def _to_source_bbox(source_bbox_dict) -> SourceBboxCoordinates:
    return _build_source_bbox_coordinates_from_dict(source_bbox_dict)


@_overloaded_build_source_bbox_coordinates_from_dict.register(list)
def _source_bbox_list(source_bbox_dict) -> list[SourceBboxCoordinates]:
    return [_build_source_bbox_coordinates_from_dict(source_bbox) for source_bbox in source_bbox_dict]


@overload
def build_source_bbox_coordinates_from_dict(source_bbox_dict: None) -> None:  # type: ignore
    pass


@overload
def build_source_bbox_coordinates_from_dict(source_bbox_dict: CommonDictType) -> SourceBboxCoordinates:
    pass


@overload
def build_source_bbox_coordinates_from_dict(  # type: ignore
    source_bbox_dict: ListOfDictsType,
) -> list[SourceBboxCoordinates]:
    pass


def build_source_bbox_coordinates_from_dict(
    source_bbox_dict: Optional[Union[CommonDictType, ListOfDictsType]],
) -> Optional[Union[SourceBboxCoordinates, list[SourceBboxCoordinates]]]:
    return _overloaded_build_source_bbox_coordinates_from_dict(source_bbox_dict)
