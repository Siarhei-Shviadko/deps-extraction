from typing import Optional

from deps_extracted_data import CharRange, SourceTextCoordinates

from ..types import CommonDictType, ListOfDictsType

__all__ = ["SourceTextCoordinatesMapper", "CharRangeMapper"]


class SourceTextCoordinatesMapper:
    @staticmethod
    def to_dict(
        source_text_coordinates: Optional[list[SourceTextCoordinates]],
    ) -> Optional[ListOfDictsType]:
        if source_text_coordinates is None:
            return None
        return [
            {
                "source_id": source_text.source_id.value,
                "char_ranges": [CharRangeMapper.to_dict(char_range) for char_range in source_text.char_ranges],
            }
            for source_text in source_text_coordinates
        ]

    @staticmethod
    def from_dict(
        source_text_coordinates_dict: Optional[ListOfDictsType],
    ) -> Optional[list[SourceTextCoordinates]]:
        if source_text_coordinates_dict is None:
            return None
        return [
            SourceTextCoordinates(
                value=source_text["source_id"],
                char_ranges=[CharRangeMapper.from_dict(char_range) for char_range in source_text["char_ranges"]],
            )
            for source_text in source_text_coordinates_dict
        ]


class CharRangeMapper:
    @staticmethod
    def to_dict(char_range: CharRange) -> CommonDictType:
        return {
            "begin": char_range.begin,
            "end": char_range.end,
        }

    @staticmethod
    def from_dict(char_range_dict: CommonDictType) -> CharRange:
        return CharRange(begin=char_range_dict["begin"], end=char_range_dict["end"])
