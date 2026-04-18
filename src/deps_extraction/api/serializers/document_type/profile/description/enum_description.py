from deps_extraction.domain.model import EnumFieldDescription

from ....configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["SerializedEnumDescription"]


class SerializedEnumDescription(ConfiguredBaseSerializer):
    options: list[str]

    def to_model(self) -> EnumFieldDescription:
        return EnumFieldDescription(options=self.options)

    @classmethod
    def from_model(cls, description: EnumFieldDescription) -> "SerializedEnumDescription":
        return cls(
            options=description.options,
        )
