from deps_extraction.domain.model import CompositeField

from ...configured_base_serializer import ConfiguredBaseSerializer
from ...document_type import SerializedField

__all__ = ["SerializedFields"]


class SerializedFields(ConfiguredBaseSerializer):
    fields: list[SerializedField]

    @classmethod
    def from_model(cls, document_type_id: str, fields: list[CompositeField]) -> "SerializedFields":
        return cls(
            fields=[
                SerializedField.from_model(
                    document_type_id=document_type_id,
                    field=field,
                )
                for field in fields
            ],
        )
